<script lang="ts">
	import type { SwingMetricsSummary } from '$lib/types';

	interface Props {
		summary: SwingMetricsSummary;
		size?: number;
	}

	let { summary, size = 300 }: Props = $props();

	const axes = $derived([
		{ label: 'Tempo', value: summary.tempo },
		{ label: 'Postur', value: summary.posture },
		{ label: 'Rotasi', value: summary.rotation },
		{ label: 'Balance', value: summary.balance },
		{ label: 'Kepala', value: summary.head_stability }
	]);

	const cx = $derived(size / 2);
	const cy = $derived(size / 2);
	const maxR = $derived(size * 0.36);
	const levels = [25, 50, 75, 100];

	function polar(index: number, value: number) {
		const angle = (Math.PI * 2 * index) / axes.length - Math.PI / 2;
		const r = (value / 100) * maxR;
		return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
	}

	function axisEnd(index: number) {
		return polar(index, 100);
	}

	const dataPoints = $derived(
		axes.map((a, i) => polar(i, a.value))
	);

	const polygon = $derived(dataPoints.map((p) => `${p.x},${p.y}`).join(' '));

	function gridPolygon(level: number) {
		return axes
			.map((_, i) => {
				const p = polar(i, level);
				return `${p.x},${p.y}`;
			})
			.join(' ');
	}
</script>

<div class="flex flex-col items-center">
	<svg width={size} height={size} viewBox="0 0 {size} {size}" class="overflow-visible">
		<!-- Grid rings -->
		{#each levels as level}
			<polygon
				points={gridPolygon(level)}
				fill="none"
				stroke="#252C35"
				stroke-width="1"
			/>
		{/each}

		<!-- Axis lines -->
		{#each axes as _, i}
			{@const end = axisEnd(i)}
			<line x1={cx} y1={cy} x2={end.x} y2={end.y} stroke="#252C35" stroke-width="1" />
		{/each}

		<!-- Data polygon -->
		<polygon
			points={polygon}
			fill="rgba(30, 122, 61, 0.2)"
			stroke="#1E7A3D"
			stroke-width="2"
			stroke-linejoin="round"
		/>

		<!-- Data points -->
		{#each dataPoints as point, i}
			<circle cx={point.x} cy={point.y} r="3.5" fill="#A6E3A1" stroke="#1E7A3D" stroke-width="1" />
			<!-- Value label near point -->
			<text
				x={point.x}
				y={point.y - 8}
				text-anchor="middle"
				class="fill-offwhite"
				font-size="10"
				font-family="Montserrat, sans-serif"
				font-weight="600"
			>
				{axes[i].value}
			</text>
		{/each}

		<!-- Axis labels -->
		{#each axes as axis, i}
			{@const labelPoint = polar(i, 118)}
			<text
				x={labelPoint.x}
				y={labelPoint.y}
				text-anchor="middle"
				dominant-baseline="middle"
				fill="#9AA3AD"
				font-size="10"
				font-family="Inter, sans-serif"
				font-weight="500"
				style="text-transform: uppercase; letter-spacing: 0.05em;"
			>
				{axis.label}
			</text>
		{/each}
	</svg>
</div>
