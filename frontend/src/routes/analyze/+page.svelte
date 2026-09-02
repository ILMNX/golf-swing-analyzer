<script lang="ts">
	import { goto } from '$app/navigation';
	import ClubSelector from '$lib/components/ClubSelector.svelte';
	import TutorialModal from '$lib/components/TutorialModal.svelte';
	import { uploadSwing, saveReport } from '$lib/api';
	import type { ClubType, ShotType } from '$lib/types';
	import { SHOT_OPTIONS } from '$lib/types';

	let club = $state<ClubType>('iron_7');
	let shotType = $state<ShotType>('full_swing');
	let videoFile = $state<File | null>(null);
	let videoPreview = $state<string | null>(null);
	let showTutorial = $state(false);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let dragOver = $state(false);

	const maxSizeMB = 100;

	function handleFileSelect(file: File | undefined) {
		error = null;
		if (!file) return;

		if (!file.type.startsWith('video/')) {
			error = 'File harus berupa video (MP4, MOV, AVI, dll.)';
			return;
		}

		if (file.size > maxSizeMB * 1024 * 1024) {
			error = `Ukuran file maksimal ${maxSizeMB} MB`;
			return;
		}

		if (videoPreview) URL.revokeObjectURL(videoPreview);
		videoFile = file;
		videoPreview = URL.createObjectURL(file);
	}

	function onFileInput(e: Event) {
		const input = e.target as HTMLInputElement;
		handleFileSelect(input.files?.[0]);
	}

	function onDrop(e: DragEvent) {
		e.preventDefault();
		dragOver = false;
		handleFileSelect(e.dataTransfer?.files?.[0]);
	}

	function removeVideo() {
		if (videoPreview) URL.revokeObjectURL(videoPreview);
		videoFile = null;
		videoPreview = null;
	}

	async function submit() {
		if (!videoFile) {
			error = 'Upload video swing terlebih dahulu';
			return;
		}

		loading = true;
		error = null;

		try {
			const result = await uploadSwing(videoFile, club, shotType);
			saveReport(result);
			await goto('/report');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Terjadi kesalahan';
		} finally {
			loading = false;
		}
	}
</script>

<section class="mx-auto max-w-6xl px-4 py-10 sm:px-6">
	<div class="mb-8 flex items-end justify-between gap-4">
		<div>
			<p class="label">Sesi Baru</p>
			<h1 class="page-title">Analisis Swing</h1>
		</div>
		<button type="button" class="btn-ghost" onclick={() => (showTutorial = true)}>
			Panduan Rekaman
		</button>
	</div>

	<form
		class="grid gap-6 lg:grid-cols-12"
		onsubmit={(e) => {
			e.preventDefault();
			submit();
		}}
	>
		<!-- Controls -->
		<div class="space-y-5 lg:col-span-4">
			<div class="card">
				<p class="label">Jenis Pukulan</p>
				<div class="space-y-1">
					{#each SHOT_OPTIONS as shot}
						<button
							type="button"
							class="w-full rounded-md border px-3 py-2.5 text-left transition
								{shotType === shot.value
								? 'border-golf bg-golf/10'
								: 'border-transparent hover:border-border'}"
							onclick={() => (shotType = shot.value)}
						>
							<p class="text-sm font-medium text-offwhite">{shot.label}</p>
							<p class="text-xs text-muted">{shot.description}</p>
						</button>
					{/each}
				</div>
			</div>

			<div class="card">
				<p class="label">Club</p>
				<ClubSelector bind:value={club} />
			</div>
		</div>

		<!-- Video -->
		<div class="lg:col-span-8">
			<div class="card h-full">
				<p class="label">Video Swing</p>

				{#if videoPreview}
					<div class="relative border border-border bg-obsidian">
						<video src={videoPreview} controls class="max-h-80 w-full object-contain">
							<track kind="captions" />
						</video>
						<button
							type="button"
							class="absolute right-2 top-2 border border-border bg-graphite px-2 py-1 text-xs text-muted hover:text-offwhite"
							onclick={removeVideo}
						>
							Hapus
						</button>
					</div>
					<p class="mt-2 truncate text-xs text-disabled">{videoFile?.name}</p>
				{:else}
					<div
						class="flex min-h-64 cursor-pointer flex-col items-center justify-center border border-dashed px-6 py-16 transition
							{dragOver ? 'border-golf bg-golf/5' : 'border-border hover:border-muted'}"
						role="button"
						tabindex="0"
						ondragover={(e) => {
							e.preventDefault();
							dragOver = true;
						}}
						ondragleave={() => (dragOver = false)}
						ondrop={onDrop}
						onclick={() => document.getElementById('video-upload')?.click()}
						onkeydown={(e) => e.key === 'Enter' && document.getElementById('video-upload')?.click()}
					>
						<svg
							width="32"
							height="32"
							viewBox="0 0 32 32"
							fill="none"
							class="mb-4 text-muted"
							aria-hidden="true"
						>
							<rect x="4" y="8" width="24" height="16" rx="2" stroke="currentColor" stroke-width="1.5"/>
							<path d="M13 14l3 3 3-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
							<path d="M16 17v-6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
						</svg>
						<p class="text-sm font-medium text-offwhite">Seret video ke sini</p>
						<p class="mt-1 text-xs text-muted">atau klik untuk memilih &middot; maks. {maxSizeMB} MB</p>
					</div>
				{/if}

				<input
					id="video-upload"
					type="file"
					accept="video/*"
					class="hidden"
					onchange={onFileInput}
				/>

				{#if error}
					<p class="mt-4 border border-error/30 bg-error/5 px-3 py-2 text-sm text-error">
						{error}
					</p>
				{/if}

				<div class="mt-6 flex justify-end border-t border-border pt-5">
					<button type="submit" class="btn-primary" disabled={loading || !videoFile}>
						{#if loading}
							<span
								class="inline-block h-3.5 w-3.5 animate-spin rounded-full border border-offwhite border-t-transparent"
							></span>
							Memproses...
						{:else}
							Analisis Swing
						{/if}
					</button>
				</div>
			</div>
		</div>
	</form>
</section>

<TutorialModal open={showTutorial} onclose={() => (showTutorial = false)} />
