import type { ClubType, ShotType, SwingAnalysis, SwingMetricsSummary } from './types';
import { CLUB_LABELS, SHOT_LABELS } from './types';

export type MetricKey = keyof SwingMetricsSummary;

export interface NextSwingAction {
	metric: MetricKey;
	label: string;
	score: number;
	priority: 'high' | 'medium';
	focus: string;
	drill: string;
}

export interface NextSwingPlan {
	actions: NextSwingAction[];
	club: string;
	shotType: string;
	clubLabel: string;
	shotLabel: string;
	analyzeUrl: string;
}

const METRIC_LABELS: Record<MetricKey, string> = {
	tempo: 'Tempo',
	posture: 'Postur',
	rotation: 'Rotasi',
	balance: 'Balance',
	head_stability: 'Kepala Stabil'
};

const BASE_DRILLS: Record<MetricKey, { focus: string; drill: string }> = {
	tempo: {
		focus: 'Rasio backswing : downswing ≈ 3 : 1',
		drill: 'Hitung frame atau ritme: 3 hitungan naik, 1 hitungan turun. Hindari rush di transisi atas.'
	},
	posture: {
		focus: 'Spine angle retention address → impact',
		drill: 'Pertahankan sudut spine (mid-hip ke mid-shoulder) konsisten. Hindari early extension atau berdiri tegak sebelum impact.'
	},
	rotation: {
		focus: 'X-factor: shoulder turn lebih besar dari hip turn',
		drill: 'Coil bahu ke belakang sambil membatasi rotasi pinggul. Targetkan selisih 20–40° pada top of swing.'
	},
	balance: {
		focus: 'Minimalkan lateral sway saat backswing',
		drill: 'Jaga mid-hip stabil relatif ke trail ankle. Transfer berat tanpa slide berlebihan ke arah target.'
	},
	head_stability: {
		focus: 'Gerak kepala minimal relatif ke lebar bahu',
		drill: 'Ukur stabilitas dari hidung/telinga. Gerak kepala <15% lebar bahu dari address ke impact.'
	}
};

const SHOT_DRILL_OVERRIDES: Partial<
	Record<ShotType, Partial<Record<MetricKey, { focus?: string; drill?: string }>>>
> = {
	full_swing: {
		rotation: {
			focus: 'Shoulder turn maksimal tanpa sway',
			drill: 'Coil ke belakang hingga bahu belakang hampir menutup target, pinggul tetap di dalam.'
		}
	},
	chip: {
		balance: {
			focus: 'Weight forward & wrist firm',
			drill: '70% berat di kaki depan. Gerakan pendek seperti putt dengan sedikit hinge pergelangan.'
		},
		head_stability: {
			focus: 'Kepala sangat stabil — minim gerakan',
			drill: 'Chip = kontrol. Kepala hampir tidak bergerak sepanjang stroke.'
		}
	},
	pitch: {
		tempo: {
			focus: 'Accelerate through impact, jangan decelerate',
			drill: 'Backswing pendek, follow-through penuh. Rasakan club "jatuh" ke bawah pada bola.'
		}
	},
	putt: {
		head_stability: {
			focus: 'Kepala benar-benar diam selama stroke',
			drill: 'Dengar impact, jangan lihat — kepala tetap di posisi hingga putter melewati bola.'
		},
		balance: {
			focus: 'Lower body seperti patung',
			drill: 'Hanya bahu & lengan bergerak. Kaki dan pinggul diam total selama putt.'
		}
	}
};

const CLUB_DRILL_OVERRIDES: Partial<
	Record<ClubType, Partial<Record<MetricKey, { focus?: string; drill?: string }>>>
> = {
	driver: {
		rotation: {
			focus: 'Turn lebar untuk jarak maksimal',
			drill: 'Backswing panjang dengan coil penuh. Lebar stance membantu rotasi tanpa kehilangan balance.'
		}
	},
	wedge: {
		balance: {
			focus: 'Kontrol weight shift minimal',
			drill: 'Wedge shot = presisi. Transfer berat halus, hindari body slide lateral.'
		}
	},
	putter: {
		tempo: {
			focus: 'Pendulum motion yang sama setiap putt',
			drill: 'Backswing dan follow-through dengan panjang yang identik — seperti bandul jam.'
		}
	}
};

function mergeDrill(
	metric: MetricKey,
	shotType: ShotType,
	club: ClubType
): { focus: string; drill: string } {
	const base = BASE_DRILLS[metric];
	const shot = SHOT_DRILL_OVERRIDES[shotType]?.[metric];
	const clubOverride = CLUB_DRILL_OVERRIDES[club]?.[metric];
	return {
		focus: clubOverride?.focus ?? shot?.focus ?? base.focus,
		drill: clubOverride?.drill ?? shot?.drill ?? base.drill
	};
}

export function getNextSwingPlan(report: SwingAnalysis): NextSwingPlan {
	const summary = report.metrics.summary;
	const shotType = report.shot_type as ShotType;
	const club = report.club as ClubType;

	const entries = (Object.entries(summary) as [MetricKey, number][]).sort((a, b) => a[1] - b[1]);

	const actions: NextSwingAction[] = entries.slice(0, 3).map(([metric, score], i) => {
		const { focus, drill } = mergeDrill(metric, shotType, club);
		return {
			metric,
			label: METRIC_LABELS[metric],
			score,
			priority: i === 0 || score < 65 ? 'high' : 'medium',
			focus,
			drill
		};
	});

	const params = new URLSearchParams({ club, shot_type: shotType });

	return {
		actions,
		club,
		shotType,
		clubLabel: CLUB_LABELS[club] ?? club,
		shotLabel: SHOT_LABELS[shotType] ?? shotType,
		analyzeUrl: `/analyze?${params.toString()}`
	};
}
