<script lang="ts">
	import { ChevronLeft, ChevronRight, X } from 'lucide';
	import Icon from '$lib/components/Icon.svelte';

	interface Props {
		open?: boolean;
		onclose?: () => void;
	}

	let { open = false, onclose }: Props = $props();

	const slides = [
		{
			title: 'Posisi Kamera',
			text: 'Setinggi pinggang, tegak lurus, jarak 2–3 meter. Rekam dari samping — face-on atau down-the-line.',
			image:
				'https://images.unsplash.com/photo-1587174485971-f9d371c0f2b9?auto=format&fit=crop&w=800&q=80',
			alt: 'Golfer melakukan swing dari sudut samping'
		},
		{
			title: 'Pencahayaan',
			text: 'Area swing harus cukup terang. Hindari backlight agar tubuh dan club terlihat jelas.',
			image:
				'https://images.unsplash.com/photo-1535131749006-b7f58c99034a?auto=format&fit=crop&w=800&q=80',
			alt: 'Lapangan golf dengan pencahayaan alami yang baik'
		},
		{
			title: 'Durasi Video',
			text: '3–8 detik mencakup address, backswing, impact, dan follow-through. Format MP4/MOV.',
			image:
				'https://images.unsplash.com/photo-1593111774240-d529f12feeb9?auto=format&fit=crop&w=800&q=80',
			alt: 'Golfer di fase backswing'
		},
		{
			title: 'Pakaian & Background',
			text: 'Pakaian kontras dengan background. Hindari orang bergerak di belakang.',
			image:
				'https://images.unsplash.com/photo-1592919505780-303950717480?auto=format&fit=crop&w=800&q=80',
			alt: 'Golfer dengan pakaian kontras di driving range'
		}
	];

	let current = $state(0);
	let touchStartX = $state(0);

	function next() {
		current = (current + 1) % slides.length;
	}

	function prev() {
		current = (current - 1 + slides.length) % slides.length;
	}

	function goTo(index: number) {
		current = index;
	}

	function handleBackdrop(e: MouseEvent) {
		if (e.target === e.currentTarget) onclose?.();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (!open) return;
		if (e.key === 'Escape') onclose?.();
		if (e.key === 'ArrowRight') next();
		if (e.key === 'ArrowLeft') prev();
	}

	function onTouchStart(e: TouchEvent) {
		touchStartX = e.touches[0].clientX;
	}

	function onTouchEnd(e: TouchEvent) {
		const diff = touchStartX - e.changedTouches[0].clientX;
		if (Math.abs(diff) > 50) {
			if (diff > 0) next();
			else prev();
		}
	}

	$effect(() => {
		if (open) current = 0;
	});
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
		<div
			class="card max-h-[92vh] w-full max-w-lg overflow-hidden rounded-b-none p-0 sm:rounded-md"
			ontouchstart={onTouchStart}
			ontouchend={onTouchEnd}
		>
			<!-- Image carousel -->
			<div class="relative aspect-[16/10] w-full overflow-hidden bg-obsidian">
				{#each slides as slide, i}
					<div
						class="absolute inset-0 transition-all duration-500 ease-out
							{i === current ? 'opacity-100 translate-x-0' : i < current ? 'opacity-0 -translate-x-full' : 'opacity-0 translate-x-full'}"
						aria-hidden={i !== current}
					>
						<img
							src={slide.image}
							alt={slide.alt}
							class="h-full w-full object-cover"
							loading="lazy"
						/>
						<div class="absolute inset-0 bg-gradient-to-t from-obsidian via-obsidian/40 to-transparent"></div>
					</div>
				{/each}

				<button
					type="button"
					class="absolute left-2 top-1/2 -translate-y-1/2 rounded-full border border-border/80 bg-obsidian/70 p-2 text-offwhite backdrop-blur-sm transition hover:bg-obsidian"
					aria-label="Slide sebelumnya"
					onclick={prev}
				>
					<Icon icon={ChevronLeft} size={18} />
				</button>
				<button
					type="button"
					class="absolute right-2 top-1/2 -translate-y-1/2 rounded-full border border-border/80 bg-obsidian/70 p-2 text-offwhite backdrop-blur-sm transition hover:bg-obsidian"
					aria-label="Slide berikutnya"
					onclick={next}
				>
					<Icon icon={ChevronRight} size={18} />
				</button>

				<button
					type="button"
					class="absolute right-3 top-3 rounded-full border border-border/80 bg-obsidian/70 p-1.5 text-muted backdrop-blur-sm transition hover:text-offwhite"
					aria-label="Tutup"
					onclick={() => onclose?.()}
				>
					<Icon icon={X} size={16} />
				</button>

				<div class="absolute bottom-3 left-4 right-4">
					<p class="text-[10px] font-bold uppercase tracking-widest text-highlight">
						{String(current + 1).padStart(2, '0')} / {String(slides.length).padStart(2, '0')}
					</p>
					<h2 id="tutorial-title" class="mt-1 font-display text-lg font-bold text-offwhite">
						{slides[current].title}
					</h2>
				</div>
			</div>

			<!-- Description -->
			<div class="px-4 py-4 sm:px-5 sm:py-5">
				<p class="text-sm leading-relaxed text-muted">{slides[current].text}</p>

				<!-- Dots -->
				<div class="mt-4 flex items-center justify-center gap-2">
					{#each slides as _, i}
						<button
							type="button"
							class="h-2 rounded-full transition-all duration-300
								{i === current ? 'w-6 bg-golf' : 'w-2 bg-border hover:bg-muted'}"
							aria-label="Ke slide {i + 1}"
							onclick={() => goTo(i)}
						></button>
					{/each}
				</div>

				<div class="mt-5 flex gap-2">
					{#if current < slides.length - 1}
						<button type="button" class="btn-primary flex-1" onclick={next}>
							Lanjut
							<Icon icon={ChevronRight} size={16} />
						</button>
					{:else}
						<button type="button" class="btn-primary flex-1" onclick={() => onclose?.()}>
							Mulai Rekam
						</button>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
