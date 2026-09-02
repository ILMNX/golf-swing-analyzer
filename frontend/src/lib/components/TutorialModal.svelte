<script lang="ts">
	interface Props {
		open?: boolean;
		onclose?: () => void;
	}

	let { open = false, onclose }: Props = $props();

	const tips = [
		{
			title: 'Posisi Kamera',
			text: 'Setinggi pinggang, tegak lurus, jarak 2–3 meter. Rekam dari samping — face-on atau down-the-line.'
		},
		{
			title: 'Pencahayaan',
			text: 'Area swing harus cukup terang. Hindari backlight agar tubuh dan club terlihat jelas.'
		},
		{
			title: 'Durasi Video',
			text: '3–8 detik mencakup address, backswing, impact, dan follow-through. Format MP4/MOV.'
		},
		{
			title: 'Pakaian & Background',
			text: 'Pakaian kontras dengan background. Hindari orang bergerak di belakang.'
		},
		{
			title: 'Konfigurasi Club',
			text: 'Pilih club dan jenis pukulan yang sesuai agar analisis akurat untuk konteks swing Anda.'
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
		class="fixed inset-0 z-50 flex items-center justify-center bg-obsidian/90 p-4"
		role="dialog"
		aria-modal="true"
		aria-labelledby="tutorial-title"
		tabindex="-1"
		onclick={handleBackdrop}
		onkeydown={handleKeydown}
	>
		<div class="card max-h-[90vh] w-full max-w-lg overflow-y-auto">
			<div class="mb-6 flex items-start justify-between gap-4">
				<div>
					<p class="label">Panduan Rekaman</p>
					<h2 id="tutorial-title" class="section-title">Persiapan Sesi</h2>
				</div>
				<button
					type="button"
					class="btn-ghost px-2"
					aria-label="Tutup"
					onclick={() => onclose?.()}
				>
					<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
						<path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
					</svg>
				</button>
			</div>

			<ol class="space-y-0 border border-border">
				{#each tips as tip, i}
					<li class="border-b border-border px-4 py-4 last:border-0">
						<p class="text-[11px] font-semibold uppercase tracking-widest text-golf">
							{String(i + 1).padStart(2, '0')}
						</p>
						<p class="mt-1 font-display text-sm font-semibold text-offwhite">{tip.title}</p>
						<p class="mt-1 text-sm leading-relaxed text-muted">{tip.text}</p>
					</li>
				{/each}
			</ol>

			<div class="mt-6 flex justify-end">
				<button type="button" class="btn-primary" onclick={() => onclose?.()}>
					Mulai Rekam
				</button>
			</div>
		</div>
	</div>
{/if}
