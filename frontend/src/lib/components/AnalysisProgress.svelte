<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { getPersonalizedTips } from '$lib/loadingTips';
	import { ANALYSIS_STAGES } from '$lib/types';
	import type { ClubType, ShotType } from '$lib/types';
	import { Loader2 } from 'lucide';
	import Icon from '$lib/components/Icon.svelte';

	interface Props {
		activeIndex?: number;
		club?: ClubType;
		shotType?: ShotType;
	}

	let { activeIndex = 0, club = 'iron_7', shotType = 'full_swing' }: Props = $props();

	let tipIndex = $state(0);
	let elapsed = $state(0);

	const tips = $derived(getPersonalizedTips(club, shotType));
	const currentTip = $derived(tips[tipIndex % tips.length]);
	const stageCount = ANALYSIS_STAGES.length;
	const progress = $derived(Math.min(95, ((activeIndex + 1) / stageCount) * 100));

	let tipTimer: ReturnType<typeof setInterval> | null = null;
	let elapsedTimer: ReturnType<typeof setInterval> | null = null;

	onMount(() => {
		tipTimer = setInterval(() => {
			tipIndex = (tipIndex + 1) % tips.length;
		}, 5000);
		elapsedTimer = setInterval(() => {
			elapsed += 1;
		}, 1000);
	});

	onDestroy(() => {
		if (tipTimer) clearInterval(tipTimer);
		if (elapsedTimer) clearInterval(elapsedTimer);
	});
</script>

<div class="card w-full max-w-md">
	<div class="mb-4 flex items-end justify-between gap-4">
		<p class="label mb-0">Proses Analisis</p>
		<span class="text-xs tabular-nums text-disabled">{elapsed}s</span>
	</div>

	<div class="mb-4 h-px w-full bg-border">
		<div class="h-px bg-golf transition-all duration-500" style="width: {progress}%"></div>
	</div>

	<ol class="space-y-0 border border-border">
		{#each ANALYSIS_STAGES as stage, i}
			<li
				class="flex items-center gap-3 border-b border-border px-4 py-3 last:border-0
					{i < activeIndex ? 'text-offwhite' : i === activeIndex ? 'text-highlight' : 'text-disabled'}"
			>
				<span class="flex h-5 w-5 shrink-0 items-center justify-center">
					{#if i < activeIndex}
						<span class="text-xs text-golf">✓</span>
					{:else if i === activeIndex}
						<Icon icon={Loader2} size={14} class="animate-spin" />
					{:else}
						<span class="text-[10px]">{i + 1}</span>
					{/if}
				</span>
				<span class="text-xs font-medium uppercase tracking-wide">{stage.label}</span>
			</li>
		{/each}
	</ol>

	<div class="mt-4 border-t border-border pt-4">
		<p class="label">Catatan</p>
		<p class="text-sm leading-relaxed text-muted">{currentTip.text}</p>
	</div>

	<p class="mt-4 text-center text-xs text-disabled">
		Analisis membutuhkan waktu 30–90 detik tergantung durasi video.
	</p>
</div>
