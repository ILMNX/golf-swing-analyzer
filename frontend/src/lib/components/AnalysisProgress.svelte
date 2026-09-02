<script lang="ts">
	import { ANALYSIS_STAGES } from '$lib/types';
	import { Loader2 } from 'lucide';
	import Icon from '$lib/components/Icon.svelte';

	interface Props {
		activeIndex?: number;
	}

	let { activeIndex = 0 }: Props = $props();
</script>

<div class="card w-full">
	<p class="label mb-4">Proses Analisis</p>
	<ol class="space-y-0 border border-border">
		{#each ANALYSIS_STAGES as stage, i}
			<li
				class="flex items-center gap-3 border-b border-border px-4 py-3 last:border-0
					{i < activeIndex ? 'text-offwhite' : i === activeIndex ? 'text-highlight' : 'text-disabled'}"
			>
				<span class="flex h-5 w-5 shrink-0 items-center justify-center">
					{#if i < activeIndex}
						<span class="text-golf text-xs">✓</span>
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
</div>
