<script lang="ts">
	import { Camera, Lightbulb, Shirt, Timer, X } from '@lucide/svelte';

	interface Props {
		open?: boolean;
		onclose?: () => void;
	}

	let { open = false, onclose }: Props = $props();

	const tips = [
		{
			icon: Camera,
			title: 'Posisi Kamera',
			text: 'Setinggi pinggang, tegak lurus, jarak 2–3 meter. Rekam dari samping — face-on atau down-the-line.'
		},
		{
			icon: Lightbulb,
			title: 'Pencahayaan',
			text: 'Area swing harus cukup terang. Hindari backlight agar tubuh dan club terlihat jelas.'
		},
		{
			icon: Timer,
			title: 'Durasi Video',
			text: '3–8 detik mencakup address, backswing, impact, dan follow-through. Format MP4/MOV.'
		},
		{
			icon: Shirt,
			title: 'Pakaian & Background',
			text: 'Pakaian kontras dengan background. Hindari orang bergerak di belakang.'
		}
	];

	function handleBackdrop(e: MouseEvent) {
		if (e.target === e.currentTarget) onclose?.();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') onclose?.();
	}
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
	<div
		class="fixed inset-0 z-50 flex items-end justify-center bg-obsidian/90 p-0 sm:items-center sm:p-4"
		role="dialog"
		aria-modal="true"
		aria-labelledby="tutorial-title"
		tabindex="-1"
		onclick={handleBackdrop}
		onkeydown={handleKeydown}
	>
		<div class="card max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-b-none sm:rounded-md">
			<div class="mb-5 flex items-start justify-between gap-4">
				<div class="min-w-0">
					<p class="label">Panduan Rekaman</p>
					<h2 id="tutorial-title" class="section-title">Persiapan Sesi</h2>
				</div>
				<button
					type="button"
					class="btn-ghost shrink-0 px-2"
					aria-label="Tutup"
					onclick={() => onclose?.()}
				>
					<X size={16} strokeWidth={1.5} />
				</button>
			</div>

			<ol class="space-y-0 border border-border">
				{#each tips as tip, i}
					{@const Icon = tip.icon}
					<li class="flex gap-3 border-b border-border px-4 py-4 last:border-0">
						<div class="flex h-8 w-8 shrink-0 items-center justify-center border border-border text-muted">
							<Icon size={15} strokeWidth={1.5} />
						</div>
						<div class="min-w-0">
							<p class="text-[11px] font-semibold uppercase tracking-wide text-golf">
								{String(i + 1).padStart(2, '0')}
							</p>
							<p class="mt-0.5 font-display text-sm font-semibold text-offwhite">{tip.title}</p>
							<p class="mt-1 text-sm leading-relaxed text-muted">{tip.text}</p>
						</div>
					</li>
				{/each}
			</ol>

			<div class="mt-5 flex justify-end sm:mt-6">
				<button type="button" class="btn-primary w-full sm:w-auto" onclick={() => onclose?.()}>
					Mulai Rekam
				</button>
			</div>
		</div>
	</div>
{/if}
