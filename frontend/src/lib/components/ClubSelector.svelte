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

<div class="space-y-5">
	{#each categories as cat}
		{@const clubs = CLUB_OPTIONS.filter((c) => c.category === cat.key)}
		{#if clubs.length > 0}
			<div>
				<p class="label">{cat.label}</p>
				<div class="flex flex-wrap gap-1.5">
					{#each clubs as club}
						<button
							type="button"
							class="rounded-md border px-3 py-1.5 text-xs font-medium uppercase tracking-wide transition
								{value === club.value
								? 'border-golf bg-golf/10 text-offwhite'
								: 'border-border text-muted hover:border-muted hover:text-offwhite'}"
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
