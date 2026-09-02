<script lang="ts">
	import type { SwingMetrics } from '$lib/types';

	interface Props {
		metrics: SwingMetrics;
	}

	let { metrics }: Props = $props();

	const items = $derived([
		{ key: 'tempo', label: 'Swing Tempo', value: metrics.tempo },
		{ key: 'posture', label: 'Postur', value: metrics.posture },
		{ key: 'rotation', label: 'Rotasi', value: metrics.rotation },
		{ key: 'balance', label: 'Keseimbangan', value: metrics.balance }
	]);

	function barColor(value: number): string {
		if (value >= 85) return 'bg-highlight';
		if (value >= 70) return 'bg-golf';
		if (value >= 55) return 'bg-warning';
		return 'bg-error';
	}
</script>

<div class="grid gap-px border border-border bg-border sm:grid-cols-2">
	{#each items as item}
		<div class="bg-graphite p-5">
			<p class="label">{item.label}</p>
			<p class="metric-value">{item.value}</p>
			<div class="mt-3 h-px w-full bg-border">
				<div
					class="h-px transition-all duration-500 {barColor(item.value)}"
					style="width: {item.value}%"
				></div>
			</div>
		</div>
	{/each}
</div>
