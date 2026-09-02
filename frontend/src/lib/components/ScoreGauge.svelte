<script lang="ts">
	interface Props {
		score: number;
		size?: 'sm' | 'lg';
	}

	let { score, size = 'lg' }: Props = $props();

	const circumference = 2 * Math.PI * 54;
	const offset = $derived(circumference - (score / 100) * circumference);

	const grade = $derived(
		score >= 90 ? 'Excellent' : score >= 75 ? 'Good' : score >= 60 ? 'Fair' : 'Needs Work'
	);

	const gradeColor = $derived(
		score >= 90
			? 'text-fairway-300'
			: score >= 75
				? 'text-fairway-400'
				: score >= 60
					? 'text-sand-300'
					: 'text-orange-400'
	);

	const strokeColor = $derived(
		score >= 90
			? '#4ade80'
			: score >= 75
				? '#22c55e'
				: score >= 60
					? '#facc15'
					: '#fb923c'
	);

	const dim = $derived(size === 'lg' ? 140 : 100);
	const fontSize = $derived(size === 'lg' ? 'text-4xl' : 'text-2xl');
</script>

<div class="flex flex-col items-center gap-2">
	<div class="relative" style="width: {dim}px; height: {dim}px;">
		<svg class="-rotate-90" width={dim} height={dim} viewBox="0 0 120 120">
			<circle cx="60" cy="60" r="54" fill="none" stroke="#14532d" stroke-width="10" />
			<circle
				cx="60"
				cy="60"
				r="54"
				fill="none"
				stroke={strokeColor}
				stroke-width="10"
				stroke-linecap="round"
				stroke-dasharray={circumference}
				stroke-dashoffset={offset}
				class="transition-all duration-700 ease-out"
			/>
		</svg>
		<div class="absolute inset-0 flex flex-col items-center justify-center">
			<span class="{fontSize} font-bold text-white">{score}</span>
			<span class="text-xs text-fairway-400">/ 100</span>
		</div>
	</div>
	<p class="text-sm font-semibold {gradeColor}">{grade}</p>
</div>
