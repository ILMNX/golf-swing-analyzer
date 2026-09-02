<script lang="ts">
	interface Props {
		open?: boolean;
		onclose?: () => void;
	}

	let { open = false, onclose }: Props = $props();

	const tips = [
		{
			icon: '📱',
			title: 'Posisi Kamera',
			text: 'Letakkan kamera setinggi pinggang, tegak lurus, dan jarak 2–3 meter dari Anda. Rekam dari samping (face-on atau down-the-line).'
		},
		{
			icon: '☀️',
			title: 'Pencahayaan',
			text: 'Pastikan area swing cukup terang. Hindari backlight agar tubuh dan club terlihat jelas di setiap frame.'
		},
		{
			icon: '🎬',
			title: 'Durasi Video',
			text: 'Rekam 3–8 detik yang mencakup address, backswing, impact, dan follow-through. Format MP4/MOV direkomendasikan.'
		},
		{
			icon: '👕',
			title: 'Pakaian & Background',
			text: 'Gunakan pakaian kontras dengan background. Hindari orang lain bergerak di belakang agar pose detection akurat.'
		},
		{
			icon: '🏌️',
			title: 'Konfigurasi Club',
			text: 'Pilih club dan jenis pukulan yang sesuai. Analisis akan disesuaikan dengan konteks swing Anda (driver vs iron vs putt).'
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
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
		role="dialog"
		aria-modal="true"
		aria-labelledby="tutorial-title"
		tabindex="-1"
		onclick={handleBackdrop}
		onkeydown={handleKeydown}
	>
		<div class="card max-h-[90vh] w-full max-w-2xl overflow-y-auto">
			<div class="mb-6 flex items-start justify-between gap-4">
				<div>
					<p class="text-sm font-medium uppercase tracking-wider text-fairway-400">Panduan</p>
					<h2 id="tutorial-title" class="font-display text-2xl font-semibold text-white">
						Tips Hasil Analisis Terbaik
					</h2>
					<p class="mt-1 text-sm text-fairway-300">
						Ikuti panduan ini sebelum merekam swing Anda.
					</p>
				</div>
				<button
					type="button"
					class="rounded-lg p-2 text-fairway-400 transition hover:bg-fairway-800 hover:text-white"
					aria-label="Tutup"
					onclick={() => onclose?.()}
				>
					✕
				</button>
			</div>

			<div class="space-y-4">
				{#each tips as tip, i}
					<div class="flex gap-4 rounded-xl border border-fairway-800 bg-fairway-950/50 p-4">
						<div
							class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-fairway-800 text-xl"
						>
							{tip.icon}
						</div>
						<div>
							<p class="font-semibold text-white">
								<span class="mr-2 text-fairway-500">{i + 1}.</span>
								{tip.title}
							</p>
							<p class="mt-1 text-sm leading-relaxed text-fairway-300">{tip.text}</p>
						</div>
					</div>
				{/each}
			</div>

			<div class="mt-6 flex justify-end">
				<button type="button" class="btn-primary" onclick={() => onclose?.()}>
					Mengerti, Mulai Rekam
				</button>
			</div>
		</div>
	</div>
{/if}
