<script lang="ts">
	import { ArrowRight, Target, Zap } from 'lucide';
	import Icon from '$lib/components/Icon.svelte';
	import { getNextSwingPlan, type NextSwingAction } from '$lib/nextSwing';
	import type { SwingAnalysis } from '$lib/types';

	interface Props {
		report: SwingAnalysis;
	}

	let { report }: Props = $props();

	const plan = $derived(getNextSwingPlan(report));

	function priorityClass(action: NextSwingAction): string {
		return action.priority === 'high'
			? 'border-golf bg-golf/10 shadow-[0_0_24px_rgba(30,122,61,0.25)]'
			: 'border-border bg-obsidian';
	}
</script>

<section class="relative mb-5 w-full min-w-0 overflow-hidden rounded-md border-2 border-golf/60 bg-gradient-to-br from-golf/15 via-graphite to-graphite p-4 sm:mb-6 sm:p-6">
	<div class="pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full bg-golf/10 blur-2xl"></div>
	<div class="pointer-events-none absolute -bottom-6 -left-6 h-24 w-24 rounded-full bg-highlight/5 blur-xl"></div>

	<div class="relative flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
		<div class="min-w-0">
			<div class="mb-2 flex items-center gap-2">
				<span class="inline-flex items-center gap-1.5 rounded-full border border-golf/50 bg-golf/20 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-widest text-highlight">
					<Icon icon={Zap} size={12} />
					Fokus Pukulan Berikutnya
				</span>
			</div>
			<h2 class="font-display text-lg font-bold text-offwhite sm:text-xl">
				Siap untuk swing berikutnya
			</h2>
			<p class="mt-1 text-sm text-muted">
				Tetap pakai <span class="font-semibold text-offwhite">{plan.shotLabel}</span>
				&middot;
				<span class="font-semibold text-offwhite">{plan.clubLabel}</span>
				— fokus pada area di bawah ini:
			</p>
		</div>
		<a href={plan.analyzeUrl} class="btn-primary shrink-0 self-start text-xs sm:text-sm">
			Rekam Pukulan Berikutnya
			<Icon icon={ArrowRight} size={15} />
		</a>
	</div>

	<div class="relative mt-5 grid gap-3 sm:grid-cols-3">
		{#each plan.actions as action, i}
			<article class="rounded-md border p-4 transition {priorityClass(action)}">
				<div class="mb-2 flex items-center justify-between gap-2">
					<div class="flex items-center gap-2">
						{#if i === 0}
							<span class="flex h-6 w-6 items-center justify-center rounded-full bg-golf text-[10px] font-bold text-offwhite">
								1
							</span>
						{:else}
							<span class="flex h-6 w-6 items-center justify-center rounded-full border border-border text-[10px] font-semibold text-muted">
								{i + 1}
							</span>
						{/if}
						<span class="text-xs font-bold uppercase tracking-wide text-highlight">{action.label}</span>
					</div>
					<span class="font-display text-lg font-bold tabular-nums {action.score < 65 ? 'text-warning' : 'text-muted'}">
						{action.score}
					</span>
				</div>
				<p class="text-sm font-semibold text-offwhite">{action.focus}</p>
				<p class="mt-2 text-xs leading-relaxed text-muted">{action.drill}</p>
				{#if action.priority === 'high'}
					<p class="mt-2 flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide text-golf">
						<Icon icon={Target} size={11} />
						Prioritas utama
					</p>
				{/if}
			</article>
		{/each}
	</div>
</section>
