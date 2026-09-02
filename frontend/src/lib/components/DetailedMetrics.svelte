<script lang="ts">
	import type { SwingMetrics } from '$lib/types';

	interface Props {
		metrics: SwingMetrics;
	}

	let { metrics }: Props = $props();

	const summaryItems = $derived([
		{ label: 'Tempo', value: metrics.summary.tempo },
		{ label: 'Postur', value: metrics.summary.posture },
		{ label: 'Rotasi', value: metrics.summary.rotation },
		{ label: 'Keseimbangan', value: metrics.summary.balance },
		{ label: 'Kepala', value: metrics.summary.head_stability }
	]);

	function barColor(value: number): string {
		if (value >= 85) return 'bg-highlight';
		if (value >= 70) return 'bg-golf';
		if (value >= 55) return 'bg-warning';
		return 'bg-error';
	}

	function formatStat(stat: { avg: number; min: number; max: number }) {
		return `${stat.avg.toFixed(1)} (min ${stat.min.toFixed(1)}, max ${stat.max.toFixed(1)})`;
	}
</script>

<!-- Summary scores -->
<div class="grid gap-px border border-border bg-border sm:grid-cols-2 lg:grid-cols-5">
	{#each summaryItems as item}
		<div class="bg-graphite p-4">
			<p class="label">{item.label}</p>
			<p class="metric-value text-2xl">{item.value}</p>
			<div class="mt-2 h-px w-full bg-border">
				<div class="h-px {barColor(item.value)}" style="width: {item.value}%"></div>
			</div>
		</div>
	{/each}
</div>

<!-- Head -->
<div class="card mt-5">
	<p class="label">Kepala</p>
	<div class="grid gap-4 sm:grid-cols-3">
		<div>
			<p class="text-xs text-muted">Stabilitas</p>
			<p class="font-display text-lg font-semibold">{metrics.head.stability_score}</p>
		</div>
		<div>
			<p class="text-xs text-muted">Gerak Lateral</p>
			<p class="font-display text-lg font-semibold">{metrics.head.lateral_movement_px} px</p>
		</div>
		<div>
			<p class="text-xs text-muted">Gerak Vertikal</p>
			<p class="font-display text-lg font-semibold">{metrics.head.vertical_movement_px} px</p>
		</div>
	</div>
</div>

<!-- Shoulders & Hips -->
<div class="mt-5 grid gap-5 lg:grid-cols-2">
	<div class="card">
		<p class="label">Pundak</p>
		<dl class="space-y-2 text-sm">
			<div class="flex justify-between gap-4">
				<dt class="text-muted">Lebar</dt>
				<dd class="text-offwhite">{formatStat(metrics.shoulders.width_px)} px</dd>
			</div>
			<div class="flex justify-between gap-4">
				<dt class="text-muted">Level Score</dt>
				<dd class="text-offwhite">{metrics.shoulders.level_score}</dd>
			</div>
			<div class="flex justify-between gap-4">
				<dt class="text-muted">Rentang Rotasi</dt>
				<dd class="text-offwhite">{metrics.shoulders.rotation_range_px} px</dd>
			</div>
		</dl>
	</div>
	<div class="card">
		<p class="label">Pinggul</p>
		<dl class="space-y-2 text-sm">
			<div class="flex justify-between gap-4">
				<dt class="text-muted">Lebar</dt>
				<dd class="text-offwhite">{formatStat(metrics.hips.width_px)} px</dd>
			</div>
			<div class="flex justify-between gap-4">
				<dt class="text-muted">Rentang Rotasi</dt>
				<dd class="text-offwhite">{metrics.hips.rotation_range_px} px</dd>
			</div>
		</dl>
	</div>
</div>

<!-- Arms & Legs -->
<div class="mt-5 grid gap-5 lg:grid-cols-2">
	<div class="card">
		<p class="label">Lengan</p>
		<dl class="space-y-2 text-sm">
			<div class="flex justify-between gap-4">
				<dt class="text-muted">Siku Kiri</dt>
				<dd class="text-offwhite">{formatStat(metrics.arms.left_elbow_angle_deg)}°</dd>
			</div>
			<div class="flex justify-between gap-4">
				<dt class="text-muted">Siku Kanan</dt>
				<dd class="text-offwhite">{formatStat(metrics.arms.right_elbow_angle_deg)}°</dd>
			</div>
			<div class="flex justify-between gap-4">
				<dt class="text-muted">Travel Pergelangan</dt>
				<dd class="text-offwhite">
					L {metrics.arms.left_wrist_travel_px}px / R {metrics.arms.right_wrist_travel_px}px
				</dd>
			</div>
		</dl>
	</div>
	<div class="card">
		<p class="label">Kaki</p>
		<dl class="space-y-2 text-sm">
			<div class="flex justify-between gap-4">
				<dt class="text-muted">Lutut Kiri</dt>
				<dd class="text-offwhite">{formatStat(metrics.legs.left_knee_angle_deg)}°</dd>
			</div>
			<div class="flex justify-between gap-4">
				<dt class="text-muted">Lutut Kanan</dt>
				<dd class="text-offwhite">{formatStat(metrics.legs.right_knee_angle_deg)}°</dd>
			</div>
			<div class="flex justify-between gap-4">
				<dt class="text-muted">Lebar Stance</dt>
				<dd class="text-offwhite">{formatStat(metrics.legs.stance_width_px)} px</dd>
			</div>
		</dl>
	</div>
</div>

<!-- Joint distances -->
<div class="card mt-5">
	<p class="label">Jarak Antar Sendi (px)</p>
	<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
		{#each Object.entries(metrics.joint_distances) as [name, stat]}
			<div class="flex justify-between gap-2 border-b border-border py-2 text-xs">
				<span class="text-muted">{name.replaceAll('_', ' ')}</span>
				<span class="text-offwhite">{stat.avg.toFixed(1)}</span>
			</div>
		{/each}
	</div>
</div>

<!-- Joint angles -->
<div class="card mt-5">
	<p class="label">Sudut Sendi (°)</p>
	<div class="grid gap-2 sm:grid-cols-2">
		{#each Object.entries(metrics.joint_angles) as [name, stat]}
			<div class="flex justify-between gap-2 border-b border-border py-2 text-xs">
				<span class="text-muted">{name.replaceAll('_', ' ')}</span>
				<span class="text-offwhite">{stat.avg.toFixed(1)}°</span>
			</div>
		{/each}
	</div>
</div>

<p class="mt-3 text-xs text-disabled">
	{metrics.frames_analyzed} frame dianalisis
</p>
