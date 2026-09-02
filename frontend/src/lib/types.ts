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

export interface SwingMetrics {
	tempo: number;
	posture: number;
	rotation: number;
	balance: number;
}

export interface SwingAnalysis {
	status: string;
	score: number;
	recommendation: string;
	club: ClubType | string;
	shot_type: ShotType | string;
	metrics: SwingMetrics;
	analyzed_at: string;
	filename: string;
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
