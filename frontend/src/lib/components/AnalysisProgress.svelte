<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { getPersonalizedTips, type LoadingTip } from '$lib/loadingTips';
	import { ANALYSIS_STAGES } from '$lib/types';
	import type { ClubType, ShotType } from '$lib/types';
	import { Check, Loader2 } from 'lucide';
	import Icon from '$lib/components/Icon.svelte';

	interface Props {
		activeIndex?: number;
		club?: ClubType;
		shotType?: ShotType;
	}

	let { activeIndex = 0, club = 'iron_7', shotType = 'full_swing' }: Props = $props();

	let tipIndex = $state(0);
	let elapsed = $state(0);
	let tipVisible = $state(true);
	let creep = $state(0);

	const tips = $derived(getPersonalizedTips(club, shotType));
	const currentTip = $derived(tips[tipIndex % tips.length]);
	const stageCount = ANALYSIS_STAGES.length;

	const progress = $derived(
		Math.min(
			96,
			((activeIndex + 0.15 + creep * 0.12) / stageCount) * 100
		)
	);

	let tipTimer: ReturnType<typeof setInterval> | null = null;
	let elapsedTimer: ReturnType<typeof setInterval> | null = null;
	let creepTimer: ReturnType<typeof setInterval> | null = null;

	function rotateTip() {
		tipVisible = false;
		setTimeout(() => {
			tipIndex = (tipIndex + 1) % tips.length;
			tipVisible = true;
		}, 280);
	}

	onMount(() => {
		tipTimer = setInterval(rotateTip, 4500);
		elapsedTimer = setInterval(() => {
			elapsed += 1;
		}, 1000);
		creepTimer = setInterval(() => {
			creep = Math.min(1, creep + 0.08);
		}, 800);
	});

	onDestroy(() => {
		if (tipTimer) clearInterval(tipTimer);
		if (elapsedTimer) clearInterval(elapsedTimer);
		if (creepTimer) clearInterval(creepTimer);
	});

	$effect(() => {
		activeIndex;
		creep = 0;
	});

	function formatElapsed(sec: number): string {
		const m = Math.floor(sec / 60);
		const s = sec % 60;
		return m > 0 ? `${m}:${String(s).padStart(2, '0')}` : `${s}s`;
	}

	function tipCategoryLabel(tip: LoadingTip): string {
		const map: Record<LoadingTip['category'], string> = {
			general: 'Info',
			technique: 'Teknik',
			recording: 'Rekaman',
			fun: 'Tahukah Kamu'
		};
		return map[tip.category];
	}
</script>

<div class="relative w-full max-w-lg overflow-hidden rounded-md border border-border bg-graphite p-5 sm:p-6">
	<!-- Ambient glow -->
	<div class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(30,122,61,0.12),transparent_60%)]"></div>

	<div class="relative">
		<!-- Header -->
		<div class="mb-5 flex items-center justify-between">
			<div>
				<p class="label mb-0">Menganalisis Swing</p>
				<p class="font-display text-sm font-semibold text-offwhite">Mohon tunggu sebentar...</p>
			</div>
			<div class="text-right">
				<p class="text-[10px] uppercase tracking-widest text-disabled">Waktu</p>
				<p class="font-display text-lg font-bold tabular-nums text-highlight">{formatElapsed(elapsed)}</p>
			</div>
		</div>

		<!-- Progress bar -->
		<div class="mb-6">
			<div class="mb-1.5 flex justify-between text-[10px] uppercase tracking-wide text-muted">
				<span>Progress</span>
				<span class="tabular-nums text-highlight">{Math.round(progress)}%</span>
			</div>
			<div class="h-2 overflow-hidden rounded-full bg-obsidian">
				<div
					class="loading-progress-bar h-full rounded-full bg-gradient-to-r from-golf to-highlight transition-all duration-700 ease-out"
					style="width: {progress}%"
				></div>
			</div>
		</div>

		<!-- Animated golf ball pulse -->
		<div class="mb-6 flex justify-center">
			<div class="loading-pulse-ring relative flex h-16 w-16 items-center justify-center">
				<div class="absolute inset-0 rounded-full border border-golf/30"></div>
				<div class="absolute inset-1 rounded-full border border-golf/20 animate-ping" style="animation-duration: 2s"></div>
				<div class="h-5 w-5 rounded-full bg-gradient-to-br from-highlight to-golf shadow-[0_0_12px_rgba(166,227,161,0.5)]"></div>
			</div>
		</div>

		<!-- Current stage -->
		<div class="mb-5 min-h-[3rem] text-center">
			{#each ANALYSIS_STAGES as stage, i}
				{#if i === activeIndex}
					<p class="loading-stage-in font-display text-base font-semibold text-offwhite sm:text-lg">
						{stage.label}
					</p>
				{/if}
			{/each}
			<p class="mt-1 text-xs text-muted">
				Tahap {activeIndex + 1} dari {stageCount}
			</p>
		</div>

		<!-- Stage pills -->
		<div class="mb-6 flex flex-wrap justify-center gap-1.5">
			{#each ANALYSIS_STAGES as stage, i}
				<span
					class="flex h-7 w-7 items-center justify-center rounded-full text-[10px] font-semibold transition-all duration-300
						{i < activeIndex
						? 'bg-golf/30 text-highlight'
						: i === activeIndex
							? 'bg-golf text-offwhite shadow-[0_0_10px_rgba(30,122,61,0.5)]'
							: 'border border-border text-disabled'}"
					title={stage.label}
				>
					{#if i < activeIndex}
						<Icon icon={Check} size={12} />
					{:else if i === activeIndex}
						<Icon icon={Loader2} size={12} class="animate-spin" />
					{:else}
						{i + 1}
					{/if}
				</span>
			{/each}
		</div>

		<!-- Timed tip carousel -->
		<div class="rounded-md border border-border/80 bg-obsidian/80 px-4 py-3">
			<div class="mb-2 flex items-center justify-between">
				<span class="text-[10px] font-bold uppercase tracking-widest text-golf">
					{tipCategoryLabel(currentTip)}
				</span>
				<span class="text-[10px] tabular-nums text-disabled">
					Tip {(tipIndex % tips.length) + 1}/{tips.length}
				</span>
			</div>
			<p
				class="min-h-[2.75rem] text-sm leading-relaxed text-offwhite transition-all duration-300
					{tipVisible ? 'loading-tip-in opacity-100' : 'opacity-0 translate-y-1'}"
			>
				{currentTip.text}
			</p>
		</div>

		<p class="mt-4 text-center text-[11px] text-disabled">
			Analisis biasanya 30–90 detik &middot; jangan tutup halaman ini
		</p>
	</div>
</div>
