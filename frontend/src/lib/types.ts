export type ClubType =
	| 'driver'
	| 'wood_3'
	| 'wood_5'
	| 'iron_3'
	| 'iron_5'
	| 'iron_7'
	| 'iron_9'
	| 'wedge'
	| 'putter';

export type ShotType = 'full_swing' | 'chip' | 'pitch' | 'putt';

export interface StatValue {
	min: number;
	max: number;
	avg: number;
	std: number;
}

export interface SwingMetricsSummary {
	tempo: number;
	posture: number;
	rotation: number;
	balance: number;
	head_stability: number;
}

export interface TuningInfo {
	version: string;
	shot_type: string;
	club: string;
	club_category: string;
	profile_id: string;
	metrics_focus: string[];
}

export interface SwingMetrics {
	summary: SwingMetricsSummary;
	biomechanics?: {
		handedness: string;
		address_frame: number;
		address_shoulder_width_px: number;
		spine_angle_address_deg: number;
		spine_angle_impact_deg: number;
		spine_angle_retention_deg: number;
		head_movement_normalized: number;
		hip_sway_px: number;
		hip_sway_normalized: number;
		shoulder_rotation_max_deg: number;
		hip_rotation_max_deg: number;
		x_factor_deg: number;
		tempo_ratio: number;
		backswing_frames: number;
		downswing_frames: number;
		lead_arm_straightness_impact_deg: number;
		top_frame: number;
		impact_frame: number;
		detection_quality: number;
	};
	posture?: {
		spine_angle_address_deg: number;
		spine_angle_impact_deg: number;
		spine_angle_retention_deg: number;
	};
	head: {
		stability_score: number;
		movement_normalized?: number;
		lateral_range_px?: number;
		vertical_range_px?: number;
		reference_shoulder_width_px?: number;
		/** @deprecated legacy pixel metric */
		lateral_movement_px?: number;
		/** @deprecated legacy pixel metric */
		vertical_movement_px?: number;
	};
	rotation?: {
		shoulder_rotation_max_deg: number;
		hip_rotation_max_deg: number;
		x_factor_deg: number;
	};
	tempo?: {
		ratio: number;
		backswing_frames: number;
		downswing_frames: number;
		top_frame: number;
		impact_frame: number;
		address_frame?: number;
	};
	balance?: {
		sway_px: number;
		sway_normalized: number;
	};
	arms?: {
		lead_arm_straightness_impact_deg?: number;
		handedness?: string;
	};
	quality?: {
		detection_quality: number;
		min_keypoint_confidence: number;
	};
	joint_distances: Record<string, StatValue>;
	joint_angles: Record<string, StatValue>;
	frames_analyzed: number;
	metrics_focus?: string[];
}

export interface AnalysisStage {
	id: string;
	label: string;
	status: string;
	duration_ms: number;
	message?: string;
}

export interface ValidationInfo {
	sharpness: number;
	visible_keypoint_ratio: number;
	person_height_ratio: number;
	sampled_frames: number;
	poses_detected: number;
	video: {
		width: number;
		height: number;
		fps: number;
		duration_sec: number;
		frame_count: number;
	};
}

export interface SwingAnalysis {
	status: string;
	score: number;
	recommendation: string;
	club: ClubType | string;
	shot_type: ShotType | string;
	metrics: SwingMetrics;
	validation?: ValidationInfo;
	tuning?: TuningInfo;
	stages?: AnalysisStage[];
	annotated_video_url?: string;
	analysis_id?: string;
	analyzed_at: string;
	filename: string;
}

export interface AnalysisError {
	status: string;
	code: string;
	error: string;
}

export interface ClubOption {
	value: ClubType;
	label: string;
	category: 'woods' | 'irons' | 'wedges' | 'putter';
}

export interface ShotOption {
	value: ShotType;
	label: string;
	description: string;
}

export const CLUB_OPTIONS: ClubOption[] = [
	{ value: 'driver', label: 'Driver', category: 'woods' },
	{ value: 'wood_3', label: '3 Wood', category: 'woods' },
	{ value: 'wood_5', label: '5 Wood', category: 'woods' },
	{ value: 'iron_3', label: '3 Iron', category: 'irons' },
	{ value: 'iron_5', label: '5 Iron', category: 'irons' },
	{ value: 'iron_7', label: '7 Iron', category: 'irons' },
	{ value: 'iron_9', label: '9 Iron', category: 'irons' },
	{ value: 'wedge', label: 'Wedge', category: 'wedges' },
	{ value: 'putter', label: 'Putter', category: 'putter' }
];

export const SHOT_OPTIONS: ShotOption[] = [
	{
		value: 'full_swing',
		label: 'Full Swing',
		description: 'Drive atau pukulan penuh dari tee/fairway'
	},
	{
		value: 'chip',
		label: 'Chip',
		description: 'Pukulan pendek dekat green'
	},
	{
		value: 'pitch',
		label: 'Pitch',
		description: 'Pukulan menengah dengan trajektori tinggi'
	},
	{
		value: 'putt',
		label: 'Putt',
		description: 'Pukulan di atas green menuju hole'
	}
];

export const CLUB_LABELS: Record<string, string> = Object.fromEntries(
	CLUB_OPTIONS.map((c) => [c.value, c.label])
);

export const SHOT_LABELS: Record<string, string> = Object.fromEntries(
	SHOT_OPTIONS.map((s) => [s.value, s.label])
);

export const ANALYSIS_STAGES = [
	{ id: 'validate', label: 'Memvalidasi video' },
	{ id: 'quality_check', label: 'Memeriksa kualitas & sudut kamera' },
	{ id: 'extract_pose', label: 'Mengekstrak pose per frame' },
	{ id: 'compute_metrics', label: 'Menghitung metrik sendi' },
	{ id: 'render_video', label: 'Membuat video analisis' },
	{ id: 'score', label: 'Menghitung skor & rekomendasi' }
];
