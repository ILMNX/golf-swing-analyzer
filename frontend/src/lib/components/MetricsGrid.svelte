<script lang="ts">
	import type { SwingMetrics } from '$lib/types';

	interface Props {
		metrics: SwingMetrics;
	}

	let { metrics }: Props = $props();

	const items = $derived([
		{ key: 'tempo', label: 'Tempo', value: metrics.tempo, icon: '⏱️' },
		{ key: 'posture', label: 'Postur', value: metrics.posture, icon: '🧍' },
		{ key: 'rotation', label: 'Rotasi', value: metrics.rotation, icon: '🔄' },
		{ key: 'balance', label: 'Keseimbangan', value: metrics.balance, icon: '⚖️' }
	]);

	function barColor(value: number): string {
		if (value >= 85) return 'bg-fairway-400';
		if (value >= 70) return 'bg-fairway-500';
		if (value >= 55) return 'bg-sand-400';
		return 'bg-orange-400';
	}
</script>

<div class="grid gap-4 sm:grid-cols-2">
	{#each items as item}
		<div class="rounded-xl border border-fairway-800 bg-fairway-950/50 p-4">
			<div class="mb-3 flex items-center justify-between">
				<div class="flex items-center gap-2">
					<span>{item.icon}</span>
					<span class="text-sm font-medium text-fairway-200">{item.label}</span>
				</div>
				<span class="text-lg font-bold text-white">{item.value}</span>
			</div>
			<div class="h-2 overflow-hidden rounded-full bg-fairway-900">
				<div
					class="h-full rounded-full transition-all duration-700 {barColor(item.value)}"
					style="width: {item.value}%"
				></div>
			</div>
		</div>
	{/each}
</div>
