<script lang="ts">
	import { getNextSwingPlan } from '$lib/nextSwing';
	import type { SwingAnalysis } from '$lib/types';

	interface Props {
		report: SwingAnalysis;
	}

	let { report }: Props = $props();

	const plan = $derived(getNextSwingPlan(report));
</script>

<div class="card mb-5 w-full min-w-0 sm:mb-6">
	<div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
		<div class="min-w-0">
			<p class="label">Pukulan Berikutnya</p>
			<p class="section-title">Fokus Latihan</p>
			<p class="mt-1 text-sm text-muted">
				{plan.shotLabel} &middot; {plan.clubLabel}
			</p>
		</div>
		<a href={plan.analyzeUrl} class="btn-primary shrink-0 self-start text-xs sm:text-sm">
			Rekam Lagi
		</a>
	</div>

	<ol class="mt-5 space-y-0 border border-border">
		{#each plan.actions as action, i}
			<li
				class="border-b border-border px-4 py-4 last:border-0
					{i === 0 ? 'border-l-2 border-l-golf bg-obsidian' : ''}"
			>
				<div class="flex items-baseline justify-between gap-4">
					<p class="text-[11px] font-semibold uppercase tracking-wide text-golf">
						{String(i + 1).padStart(2, '0')} &middot; {action.label}
					</p>
					<p
						class="font-display text-lg font-semibold tabular-nums
							{action.score < 65 ? 'text-warning' : 'text-offwhite'}"
					>
						{action.score}
					</p>
				</div>
				<p class="mt-2 text-sm text-offwhite">{action.focus}</p>
				<p class="mt-1 text-sm leading-relaxed text-muted">{action.drill}</p>
			</li>
		{/each}
	</ol>
</div>
