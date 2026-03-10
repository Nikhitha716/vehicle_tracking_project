# Mikel Broström 🔥 BoxMOT 🧾 AGPL-3.0 license

from functools import partial
from pathlib import Path

import cv2
import numpy as np
import torch
import json
import os

from boxmot import TRACKERS
from boxmot.detectors import (default_imgsz, get_yolo_inferer,
                              is_ultralytics_model)
from boxmot.trackers.tracker_zoo import create_tracker
from boxmot.utils import TRACKER_CONFIGS
from boxmot.utils import logger as LOGGER
from boxmot.utils.checks import RequirementsChecker
from boxmot.utils.timing import TimingStats, wrap_tracker_reid

checker = RequirementsChecker()
checker.check_packages(("ultralytics", ))  # install

from ultralytics import YOLO
from boxmot.addons.occlusion.occlusion_state import OcclusionState

from boxmot.addons.occlusion.occlusion_logger import OcclusionLogger

from boxmot.addons.occlusion.occlusion_state import OcclusionState
from boxmot.addons.occlusion.occlusion_visuals import (
    draw_trajectory,
    draw_occlusion_text,
)
from boxmot.addons.occlusion.occlusion_config import (
    MIN_OCCLUSION_FRAMES,
    MAX_OCCLUSIONS_TO_DRAW,
)

from boxmot.addons.occlusion.occlusion_visuals import draw_occlusion_panel

from boxmot.addons.prediction.behavior_predictor import BehaviorPredictor
from boxmot.addons.prediction.prediction_logger import PredictionLogger
from boxmot.addons.prediction.prediction_config import (
    PREDICTION_INTERVAL,
    ENABLE_PREDICTION,
)

from boxmot.addons.planning.risk_assessor import RiskAssessor
from boxmot.addons.planning.planning_logger import PlanningLogger
from boxmot.addons.planning.planning_config import ENABLE_PLANNING









class VideoWriter:
    """Handles video writing for tracking results."""
    
    def __init__(self, output_path, fps=30):
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.fps = fps
        self.writer = None
        self.frame_size = None
    
    def write(self, frame):
        """Write a frame to the video."""
        if self.writer is None:
            h, w = frame.shape[:2]
            self.frame_size = (w, h)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.writer = cv2.VideoWriter(
                str(self.output_path), fourcc, self.fps, self.frame_size
            )
            LOGGER.opt(colors=True).info(f"<bold>Saving video to:</bold> <cyan>{self.output_path}</cyan>")
        
        self.writer.write(frame)
    
    def release(self):
        """Release the video writer."""
        if self.writer is not None:
            self.writer.release()
            LOGGER.opt(colors=True).info(f"<bold>Video saved:</bold> <cyan>{self.output_path}</cyan>")


def on_predict_start(predictor, args, timing_stats=None):
    """
    Initialize trackers for object tracking during prediction.
    
    Args:
        predictor (object): The predictor object to initialize trackers for.
        args: CLI arguments containing tracking configuration.
        timing_stats: Optional TimingStats for ReID timing instrumentation.
    """
    assert args.tracking_method in TRACKERS, \
        f"'{args.tracking_method}' is not supported. Supported ones are {TRACKERS}"

    tracking_config = TRACKER_CONFIGS / (args.tracking_method + '.yaml')
    trackers = []
    # Ensure at least 1 tracker is created (bs might be 0 for some sources)
    batch_size = max(1, predictor.dataset.bs)
    for i in range(batch_size):
        tracker = create_tracker(
            args.tracking_method,
            tracking_config,
            args.reid_model,
            predictor.device,
            args.half,
            args.per_class,
        )
        # set target_id if user passed it
        if args.target_id is not None:
            tracker.target_id = args.target_id
        
        # Wrap ReID model for timing instrumentation
        if timing_stats is not None:
            wrap_tracker_reid(tracker, timing_stats)
        
        trackers.append(tracker)

    predictor.trackers = trackers
    predictor.custom_args = args  # Store for later use
    # ---------- OCCLUSION ADDON INIT (STEP 4.2) ----------
    if getattr(args, "enable_occlusion_addon", False):
        predictor.occlusion_state = OcclusionState()
    # Initialize lane state (once per run)
    from boxmot.addons.lane_validation.lane_state import LaneState
    predictor.lane_state = LaneState()

    # ----------------------------------------------------
     


def plot_trajectories(predictor, timing_stats=None, video_writer=None):
    """
    Callback to run tracking update and plot trajectories on each frame.
    """

    # frame counter
    if not hasattr(predictor, "_frame_index"):
        predictor._frame_index = 0
    # Initialize prediction modules (once)
    if ENABLE_PREDICTION and not hasattr(predictor, "behavior_predictor"):
        predictor.behavior_predictor = BehaviorPredictor()
        predictor.prediction_logger = PredictionLogger(predictor.save_dir)

    # Initialize planning modules (once)
    if ENABLE_PLANNING and not hasattr(predictor, "risk_assessor"):
        predictor.risk_assessor = RiskAssessor()
        predictor.planning_logger = PlanningLogger(predictor.save_dir)



    # safety check
    if not hasattr(predictor, "trackers") or not predictor.trackers:
        return

    for i, result in enumerate(predictor.results):
        if i >= len(predictor.trackers):
            continue

        tracker = predictor.trackers[i]
        img = result.orig_img
        dets = result.boxes.data.cpu().numpy() if result.boxes is not None else []

        # timing
        if timing_stats:
            timing_stats.reset_frame_reid()
            timing_stats.start_tracking()

        tracks = tracker.update(dets, img)

        # -------- LANE ASSIGNMENT (STEP 1.4) --------
        from boxmot.addons.lane_validation.lane_assigner import assign_lane_id

        if tracks is not None and hasattr(predictor, "lane_state"):
            img_h, img_w = img.shape[:2]
            frame_idx = predictor._frame_index

            for t in tracks:
                x1, y1, x2, y2, track_id = map(int, t[:5])
                cx = (x1 + x2) // 2

                lane_id = assign_lane_id(cx, img_w)

                predictor.lane_state.update(
                    track_id=track_id,
                    lane_id=lane_id,
                    frame_idx=frame_idx
                )
# -------------------------------------------
        # -------- LANE VALIDATION (STEP 1.5) --------
        from boxmot.addons.lane_validation.lane_validator import validate_lane_transition

        if hasattr(predictor, "lane_state"):
            for t in tracks:
                track_id = int(t[4])

                prev_lane = predictor.lane_state.get_previous_lane(track_id)
                curr_lane = predictor.lane_state.get_current_lane(track_id)

                event = validate_lane_transition(
                    track_id, prev_lane, curr_lane
                )

                # Lazy init logger
                if not hasattr(predictor, "lane_logger"):
                    from boxmot.addons.lane_validation.lane_logger import LaneEventLogger
                    predictor.lane_logger = LaneEventLogger(predictor.save_dir)

                predictor.lane_logger.log(
                    frame=predictor._frame_index,
                    track_id=track_id,
                    prev_lane=prev_lane,
                    curr_lane=curr_lane,
                    event_type=event
                )

                # Subtle visual cue (only on violation)
                if event == "LANE_JUMP":
                    x1, y1, _, _ = map(int, t[:4])
                    cv2.putText(
                        img,
                        "Lane jump",
                        (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 255),
                        1
                    )
# -------------------------------------------
        # -------- UNCERTAINTY-AWARE PREDICTION (STEP 2.4) --------
        if ENABLE_PREDICTION and hasattr(predictor, "lane_state"):
            frame_idx = predictor._frame_index

            # Run prediction every N frames
            if frame_idx % PREDICTION_INTERVAL == 0:
                for t in tracks:
                    x1, y1, x2, y2, track_id = map(int, t[:5])
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2

                    # Compute simple speed (pixels/frame)
                    prev_pos = predictor.occlusion_state.last_positions.get(track_id)
                    if prev_pos is None:
                        speed = 0.0
                    else:
                        px, py = prev_pos
                        speed = ((cx - px) ** 2 + (cy - py) ** 2) ** 0.5

                    curr_lane = predictor.lane_state.get_current_lane(track_id)
                    prev_lane = predictor.lane_state.get_previous_lane(track_id)

                    probs = predictor.behavior_predictor.predict(
                        track_id=track_id,
                        curr_lane=curr_lane,
                        prev_lane=prev_lane,
                        speed=speed,
                    )

                    predictor.prediction_logger.log(
                        frame=frame_idx,
                        track_id=track_id,
                        probs=probs,
                    )
# --------------------------------------------------------
        # -------- RISK-SENSITIVE PLANNING (STEP 3.4) --------
        if ENABLE_PLANNING:
            frame_idx = predictor._frame_index

            for t in tracks:
                track_id = int(t[4])

                # Fetch last prediction for this track
                if track_id not in predictor.behavior_predictor.prev_speed:
                    continue  # skip if no prediction yet

                # Get latest prediction probabilities
                probs = predictor.behavior_predictor.predict(
                    track_id=track_id,
                    curr_lane=predictor.lane_state.get_current_lane(track_id),
                    prev_lane=predictor.lane_state.get_previous_lane(track_id),
                    speed=0.0,  # speed already accounted earlier
                )

                risk_level, advisory = predictor.risk_assessor.assess(probs)

                predictor.planning_logger.log(
                    frame=frame_idx,
                    track_id=track_id,
                    risk_level=risk_level,
                    advisory=advisory,
                )
        # ---------------------------------------------------


        # ---- FRAME-WISE LOGGING (RESTORE TERMINAL OUTPUT) ----
        n_tracks = len(tracks) if tracks is not None else 0

        LOGGER.info(
            f"Frame {predictor._frame_index} | "
            f"Active IDs: {n_tracks}"
        )
# -----------------------------------------------------


        # ---------------- OCCLUSION ADDON (STABLE) ----------------
        if predictor.custom_args.enable_occlusion_addon:
            visible_ids = set()

            if tracks is not None:
                for t in tracks:
                    x1, y1, x2, y2, tid = map(int, t[:5])
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                    predictor.occlusion_state.update_visible(tid, (cx, cy))

                    log_entry = {
                        "frame": predictor._frame_index,
                        "track_id": tid,
                        "status": "reappeared"
                    }

                    BASE_DIR = os.path.dirname(
                        os.path.dirname(
                            os.path.dirname(
                                os.path.dirname(os.path.abspath(__file__))
                            )
                         )
                    )

                    LOG_PATH = os.path.join(BASE_DIR, "logs", "occlusion_log.json")

                    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

                    if not os.path.exists(LOG_PATH):
                        with open(LOG_PATH, "w") as f:
                            f.write("[]")

                    with open(LOG_PATH, "r+") as f:
                        data = json.load(f)
                        data.append(log_entry)
                        f.seek(0)
                        json.dump(data, f, indent=2)

                    visible_ids.add(tid)

                    # draw trajectory (WHITE)
                    draw_trajectory(
                        img,
                        predictor.occlusion_state.trajectories[tid]
                    )

            # mark missed
            for tid in list(predictor.occlusion_state.last_positions.keys()):
                if tid not in visible_ids:
                    predictor.occlusion_state.mark_missed(tid)

                    # show occlusion label
                    if predictor.occlusion_state.is_occluded(tid):
                        pos = predictor.occlusion_state.last_positions[tid]
                        log_entry = {
                            "frame": predictor._frame_index,
                            "track_id": tid,
                            "status": "occluded"
                        }

                        BASE_DIR = os.path.dirname(
                            os.path.dirname(
                                os.path.dirname(
                                    os.path.dirname(os.path.abspath(__file__))
                                )
                            )
                        )

                        LOG_PATH = os.path.join(BASE_DIR, "logs", "occlusion_log.json")

                        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

                        if not os.path.exists(LOG_PATH):
                            with open(LOG_PATH, "w") as f:
                                f.write("[]")

                        with open(LOG_PATH, "r+") as f:
                            data = json.load(f)
                            data.append(log_entry)
                            f.seek(0)
                            json.dump(data, f, indent=2)
                        #draw_occlusion_text(img, tid, pos)
        # ----------------------------------------------------------

        if timing_stats:
            timing_stats.end_tracking()

        # base plotting (disable default trajs)
        show_traj = False if predictor.custom_args.enable_occlusion_addon else predictor.custom_args.show_trajectories

        result.orig_img = tracker.plot_results(
            img,
            show_traj,
            show_lost=predictor.custom_args.show_lost
        )
        # -------- OCCLUSION ADDON: RIGHT-TOP PANEL --------
        if predictor.custom_args.enable_occlusion_addon:
            h, w = result.orig_img.shape[:2]

            x0 = w - 260   # panel X (right side)
            y0 = 30        # panel Y (top)
            line_h = 22

            cv2.putText(
                result.orig_img,
                "Occluded IDs:",
                (x0, y0),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 165, 255),  # orange
                2
            )

            row = 1
            MAX_PANEL_MISSING_FRAMES = 30  # show only short occlusions

            for tid in sorted(predictor.occlusion_state.last_positions.keys()):
                missed = predictor.occlusion_state.missed_counts.get(tid, 0)

                # Show only TEMPORARY occlusions, not exits
                if predictor.occlusion_state.is_occluded(tid) and missed <= MAX_PANEL_MISSING_FRAMES:
                    cv2.putText(
                        result.orig_img,
                        f"ID {tid}",
                        (x0, y0 + row * line_h),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 0),
                        2
                    )
                    row += 1

# -------------------------------------------------


        if video_writer:
            video_writer.write(result.orig_img)

        if predictor.custom_args.show:
            cv2.imshow("BoxMOT", result.orig_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                predictor.custom_args._user_quit = True

    predictor._frame_index += 1




def setup_yolox_model(predictor, args, yolo_model_instance):
    """
    Setup YOLOX model by replacing the predictor's model with our custom inferer.
    Called via on_predict_start callback.
    
    Args:
        predictor: The Ultralytics predictor object.
        args: CLI arguments.
        yolo_model_instance: The YoloXStrategy instance to use.
    """
    # Replace the YOLO model with our custom inferer
    predictor.model = yolo_model_instance

    # Override preprocess and postprocess for non-ultralytics models
    predictor.preprocess = lambda imgs: yolo_model_instance.preprocess(im=imgs)
    predictor.postprocess = lambda preds, im, im0s: yolo_model_instance.postprocess(
        preds=preds, im=im, im0s=im0s
    )


@torch.no_grad()
def main(args):
    """
    Run tracking using the integrated Ultralytics workflow.
    
    Args:
        args: Arguments from CLI (SimpleNamespace from cli.py)
    """
    # Print tracking pipeline header (blue palette)
    LOGGER.info("")
    LOGGER.opt(colors=True).info("<blue>" + "="*60 + "</blue>")
    LOGGER.opt(colors=True).info("<bold><cyan>🎯 BoxMOT Tracking Pipeline</cyan></bold>")
    LOGGER.opt(colors=True).info("<blue>" + "="*60 + "</blue>")
    LOGGER.opt(colors=True).info(f"<bold>Detector:</bold>  <cyan>{args.yolo_model}</cyan>")
    LOGGER.opt(colors=True).info(f"<bold>ReID:</bold>      <cyan>{args.reid_model}</cyan>")
    LOGGER.opt(colors=True).info(f"<bold>Tracker:</bold>   <cyan>{args.tracking_method}</cyan>")
    LOGGER.opt(colors=True).info(f"<bold>Source:</bold>    <cyan>{args.source}</cyan>")
    LOGGER.opt(colors=True).info("<blue>" + "="*60 + "</blue>")
    
    # Set default image size based on model type
    if args.imgsz is None:
        args.imgsz = default_imgsz(args.yolo_model)
    
    # Initialize timing stats
    timing_stats = TimingStats()
    
    # Initialize video writer if saving is enabled
    video_writer = None
    if args.save:
        # Determine output path
        project = Path(args.project) if args.project else Path("runs/track")
        name = args.name if args.name else "exp"
        save_dir = project / name
        
        # Handle exist_ok
        if not args.exist_ok:
            i = 1
            while save_dir.exists():
                save_dir = project / f"{name}{i}"
                i += 1
        
        # Determine video filename from source
        source_path = Path(args.source)
        if source_path.is_file():
            video_name = source_path.stem + "_tracked.mp4"
        elif source_path.is_dir():
            video_name = source_path.name + "_tracked.mp4"
        else:
            video_name = "tracking_output.mp4"
        
        video_writer = VideoWriter(save_dir / video_name, fps=30)
    
    # Initialize YOLO model (use placeholder if non-ultralytics model)
    yolo = YOLO(
        args.yolo_model if is_ultralytics_model(args.yolo_model) else "yolov8n.pt",
    )

    # Add callbacks for tracker initialization and trajectory plotting
    # Pass args, timing_stats and video_writer through partial to make them available in callbacks
    yolo.add_callback("on_predict_start", partial(on_predict_start, args=args, timing_stats=timing_stats))
    yolo.add_callback("on_predict_postprocess_end", partial(plot_trajectories, timing_stats=timing_stats, video_writer=video_writer))
    
    # Add callback to start frame timing
    yolo.add_callback("on_predict_batch_start", lambda p: timing_stats.start_frame())

    # Handle non-ultralytics models (e.g., YOLOX)
    # We need to setup the model replacement via callback since predictor
    # doesn't exist until predict() is called
    yolox_model = None
    if not is_ultralytics_model(args.yolo_model):
        # Create the YOLOX model inferer - will be setup in callback
        m = get_yolo_inferer(args.yolo_model)
        
        # Define a callback that will setup YOLOX when predictor is ready
        def setup_yolox_callback(predictor):
            nonlocal yolox_model
            yolox_model = m(
                model=args.yolo_model,
                device=predictor.device,
                args=predictor.args,
            )
            setup_yolox_model(predictor, args, yolox_model)
        
        # Add the setup callback - it will run on_predict_start
        yolo.add_callback("on_predict_start", setup_yolox_callback)
        
        # Add callback to save image paths for further processing
        def update_paths_callback(predictor):
            if yolox_model is not None:
                yolox_model.update_im_paths(predictor)
        yolo.add_callback("on_predict_batch_start", update_paths_callback)

    # Use predict() instead of track() to avoid Ultralytics' default tracking callbacks
    results = yolo.predict(
        source=args.source,
        conf=args.conf,
        iou=args.iou,
        agnostic_nms=args.agnostic_nms,
        show=False,
        stream=True,
        device=args.device,
        show_conf=args.show_conf,
        save_txt=args.save_txt,
        show_labels=args.show_labels,
        save=False,  # We handle video saving ourselves with tracking overlays
        verbose=args.verbose,
        exist_ok=args.exist_ok,
        project=args.project,
        name=args.name,
        classes=args.classes,
        imgsz=args.imgsz,
        vid_stride=args.vid_stride,
        line_width=args.line_width,
        save_crop=args.save_crop,
    )

    # Initialize quit flag
    args._user_quit = False
    
    # Iterate through results to run the tracking pipeline
    try:
        for result in results:
            # Check if user requested quit
            if args._user_quit:
                break
                
            # Record Ultralytics timing from result.speed (populated after yield)
            if hasattr(result, 'speed') and result.speed:
                timing_stats.totals['preprocess'] += result.speed.get('preprocess', 0) or 0
                timing_stats.totals['inference'] += result.speed.get('inference', 0) or 0
                timing_stats.totals['postprocess'] += result.speed.get('postprocess', 0) or 0
    except KeyboardInterrupt:
        pass  # Handle Ctrl+C gracefully
    finally:
        # Release video writer
        if video_writer is not None:
            video_writer.release()
        # Always print timing summary when done
        timing_stats.print_summary()
        # Clean up windows
        cv2.destroyAllWindows()


if __name__ == "__main__":
    raise SystemExit("Run via CLI: boxmot track [options]")
