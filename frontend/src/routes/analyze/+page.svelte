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
			error = 'Silakan upload video swing terlebih dahulu';
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

<section class="mx-auto max-w-3xl px-4 py-10 sm:px-6">
	<div class="mb-8">
		<h1 class="font-display text-3xl font-semibold text-white">Analisis Swing</h1>
		<p class="mt-2 text-fairway-400">
			Upload video, konfigurasi club, lalu kirim untuk dianalisis oleh AI.
		</p>
	</div>

	<!-- Tutorial banner -->
	<div
		class="mb-6 flex flex-col gap-3 rounded-xl border border-sand-500/30 bg-sand-500/10 p-4 sm:flex-row sm:items-center sm:justify-between"
	>
		<div class="flex items-start gap-3">
			<span class="text-xl">💡</span>
			<div>
				<p class="font-medium text-sand-200">Belum pernah merekam?</p>
				<p class="text-sm text-sand-300/80">Baca panduan singkat untuk hasil analisis terbaik.</p>
			</div>
		</div>
		<button type="button" class="btn-secondary shrink-0 text-sm" onclick={() => (showTutorial = true)}>
			Lihat Panduan
		</button>
	</div>

	<form
		class="space-y-6"
		onsubmit={(e) => {
			e.preventDefault();
			submit();
		}}
	>
		<!-- Video upload -->
		<div class="card">
			<label class="label" for="video-upload">Video Swing</label>

			{#if videoPreview}
				<div class="relative overflow-hidden rounded-xl border border-fairway-700">
					<video src={videoPreview} controls class="max-h-64 w-full bg-black object-contain">
						<track kind="captions" />
					</video>
					<button
						type="button"
						class="absolute right-3 top-3 rounded-lg bg-black/60 px-3 py-1 text-sm text-white backdrop-blur hover:bg-black/80"
						onclick={removeVideo}
					>
						Hapus
					</button>
				</div>
				<p class="mt-2 text-xs text-fairway-500">{videoFile?.name}</p>
			{:else}
				<div
					class="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-12 transition
						{dragOver
						? 'border-fairway-400 bg-fairway-800/30'
						: 'border-fairway-700 bg-fairway-950/40 hover:border-fairway-500'}"
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
					<span class="mb-3 text-4xl">🎬</span>
					<p class="font-medium text-fairway-200">Seret & lepas video di sini</p>
					<p class="mt-1 text-sm text-fairway-500">atau klik untuk memilih file (maks. {maxSizeMB} MB)</p>
				</div>
			{/if}

			<input
				id="video-upload"
				type="file"
				accept="video/*"
				class="hidden"
				onchange={onFileInput}
			/>
		</div>

		<!-- Shot type -->
		<div class="card">
			<p class="label">Jenis Pukulan</p>
			<div class="grid gap-3 sm:grid-cols-2">
				{#each SHOT_OPTIONS as shot}
					<button
						type="button"
						class="rounded-xl border p-4 text-left transition
							{shotType === shot.value
							? 'border-fairway-400 bg-fairway-800/60'
							: 'border-fairway-700 bg-fairway-950/40 hover:border-fairway-600'}"
						onclick={() => (shotType = shot.value)}
					>
						<p class="font-semibold text-white">{shot.label}</p>
						<p class="mt-1 text-xs text-fairway-400">{shot.description}</p>
					</button>
				{/each}
			</div>
		</div>

		<!-- Club selector -->
		<div class="card">
			<p class="label">Pilih Club</p>
			<ClubSelector bind:value={club} />
		</div>

		{#if error}
			<div class="rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-300">
				{error}
			</div>
		{/if}

		<div class="flex flex-col gap-3 sm:flex-row sm:justify-end">
			<button
				type="button"
				class="btn-secondary"
				onclick={() => (showTutorial = true)}
				disabled={loading}
			>
				📖 Panduan
			</button>
			<button type="submit" class="btn-primary" disabled={loading || !videoFile}>
				{#if loading}
					<span
						class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"
					></span>
					Menganalisis...
				{:else}
					Analisis Swing →
				{/if}
			</button>
		</div>
	</form>
</section>

<TutorialModal open={showTutorial} onclose={() => (showTutorial = false)} />
