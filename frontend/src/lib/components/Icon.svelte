<script lang="ts">
	import type { IconNode } from 'lucide';

	interface Props {
		icon: IconNode;
		size?: number;
		strokeWidth?: number;
		class?: string;
	}

	let { icon, size = 16, strokeWidth = 1.5, class: className = '' }: Props = $props();
</script>

<svg
	xmlns="http://www.w3.org/2000/svg"
	width={size}
	height={size}
	viewBox="0 0 24 24"
	fill="none"
	stroke="currentColor"
	stroke-width={strokeWidth}
	stroke-linecap="round"
	stroke-linejoin="round"
	class={className}
	aria-hidden="true"
>
	{#each icon as [tag, attrs]}
		<svelte:element this={tag} {...attrs} />
	{/each}
</svg>
