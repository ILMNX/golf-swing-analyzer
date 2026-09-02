<script lang="ts">
	interface Props {
		score: number;
		size?: 'sm' | 'lg';
	}

	let { score, size = 'lg' }: Props = $props();

	const circumference = 2 * Math.PI * 46;
	const offset = $derived(circumference - (score / 100) * circumference);

	const grade = $derived(
		score >= 90 ? 'Excellent' : score >= 75 ? 'Good' : score >= 60 ? 'Fair' : 'Needs Work'
	);

	const dim = $derived(size === 'lg' ? 120 : 88);
	const fontSize = $derived(size === 'lg' ? 'text-4xl' : 'text-2xl');
</script>

<div>
	<div class="relative" style="width: {dim}px; height: {dim}px;">
		<svg class="-rotate-90" width={dim} height={dim} viewBox="0 0 100 100">
			<circle cx="50" cy="50" r="46" fill="none" stroke="#252C35" stroke-width="2" />
			<circle
				cx="50"
				cy="50"
				r="46"
				fill="none"
				stroke="#1E7A3D"
				stroke-width="2"
				stroke-linecap="round"
				stroke-dasharray={circumference}
				stroke-dashoffset={offset}
				class="transition-all duration-500 ease-out"
			/>
		</svg>
		<div class="absolute inset-0 flex flex-col items-center justify-center">
			<span class="{fontSize} font-display font-bold tabular-nums text-offwhite">{score}</span>
		</div>
	</div>
	<p class="mt-2 text-[11px] font-semibold uppercase tracking-widest text-muted">Overall Score</p>
	<p class="text-xs text-highlight">{grade}</p>
</div>
