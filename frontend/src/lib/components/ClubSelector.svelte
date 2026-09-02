<script lang="ts">
	import type { ClubType } from '$lib/types';
	import { CLUB_OPTIONS } from '$lib/types';

	interface Props {
		value?: ClubType;
		onchange?: (club: ClubType) => void;
	}

	let { value = $bindable('iron_7' as ClubType), onchange }: Props = $props();

	const categories = [
		{ key: 'woods', label: 'Woods' },
		{ key: 'irons', label: 'Irons' },
		{ key: 'wedges', label: 'Wedges' },
		{ key: 'putter', label: 'Putter' }
	] as const;

	function select(club: ClubType) {
		value = club;
		onchange?.(club);
	}
</script>

<div class="space-y-4">
	{#each categories as cat}
		{@const clubs = CLUB_OPTIONS.filter((c) => c.category === cat.key)}
		{#if clubs.length > 0}
			<div>
				<p class="mb-2 text-xs font-semibold uppercase tracking-wider text-fairway-500">
					{cat.label}
				</p>
				<div class="flex flex-wrap gap-2">
					{#each clubs as club}
						<button
							type="button"
							class="rounded-xl border px-4 py-2 text-sm font-medium transition
								{value === club.value
								? 'border-fairway-400 bg-fairway-700 text-white shadow-md'
								: 'border-fairway-700 bg-fairway-950/50 text-fairway-300 hover:border-fairway-500'}"
							onclick={() => select(club.value)}
						>
							{club.label}
						</button>
					{/each}
				</div>
			</div>
		{/if}
	{/each}
</div>
