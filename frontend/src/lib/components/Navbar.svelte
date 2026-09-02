<script lang="ts">
	import { page } from '$app/stores';

	const links = [
		{ href: '/', label: 'Beranda' },
		{ href: '/analyze', label: 'Analisis' },
		{ href: '/report', label: 'Laporan' }
	];
</script>

<header class="sticky top-0 z-40 border-b border-fairway-800/60 bg-fairway-950/80 backdrop-blur-md">
	<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
		<a href="/" class="flex items-center gap-3">
			<div
				class="flex h-10 w-10 items-center justify-center rounded-xl bg-fairway-700 text-lg font-bold text-sand-300"
			>
				⛳
			</div>
			<div>
				<p class="font-display text-lg font-semibold leading-tight text-white">SwingPro</p>
				<p class="text-xs text-fairway-400">Golf Swing Analyzer</p>
			</div>
		</a>

		<nav class="flex items-center gap-1 sm:gap-2">
			{#each links as link}
				<a
					href={link.href}
					class="rounded-lg px-3 py-2 text-sm font-medium transition sm:px-4
						{$page.url.pathname === link.href
						? 'bg-fairway-800 text-white'
						: 'text-fairway-300 hover:bg-fairway-900 hover:text-white'}"
				>
					{link.label}
				</a>
			{/each}
		</nav>
	</div>
</header>
