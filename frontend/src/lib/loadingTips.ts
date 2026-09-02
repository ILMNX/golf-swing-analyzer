import type { ClubType, ShotType } from './types';
import { CLUB_LABELS, SHOT_LABELS } from './types';

export interface LoadingTip {
	text: string;
	category: 'general' | 'technique' | 'recording' | 'fun';
}

export const LOADING_TIPS: LoadingTip[] = [
	{ text: 'Rekam dari samping agar rotasi bahu & pinggul terlihat jelas.', category: 'recording' },
	{ text: 'Durasi ideal 5–8 detik — cukup untuk satu swing penuh.', category: 'recording' },
	{ text: 'Tempo yang baik: backswing 3 hitungan, downswing 1 hitungan.', category: 'technique' },
	{ text: 'Kepala stabil = kontak lebih konsisten. Jangan angkat terlalu cepat.', category: 'technique' },
	{ text: 'Finish seimbang di kaki depan menandakan weight transfer yang benar.', category: 'technique' },
	{ text: 'Pakaian kontras dengan background membantu AI mendeteksi pose.', category: 'recording' },
	{ text: 'Pro player rata-rata backswing 0.75 detik — tidak perlu terburu-buru.', category: 'fun' },
	{ text: 'Latihan mirror 5 menit sebelum rekam bisa meningkatkan postur.', category: 'technique' },
	{ text: 'Hindari backlight — wajah & tubuh harus lebih terang dari background.', category: 'recording' },
	{ text: 'Konsistensi lebih penting dari jarak. Ulangi swing yang sama.', category: 'general' },
	{ text: 'Sistem memetakan 17 titik sendi untuk menghitung metrik swing.', category: 'general' },
	{ text: 'Setiap swing adalah data. Analisis ini bantu kamu iterasi lebih cepat.', category: 'general' }
];

export function getPersonalizedTips(club: ClubType, shotType: ShotType): LoadingTip[] {
	const clubLabel = CLUB_LABELS[club] ?? club;
	const shotLabel = SHOT_LABELS[shotType] ?? shotType;

	const personalized: LoadingTip[] = [
		{
			text: `${shotLabel} · ${clubLabel} — profil analisis disesuaikan untuk kombinasi ini.`,
			category: 'general'
		}
	];

	if (shotType === 'putt') {
		personalized.push({
			text: 'Putt: fokus pada stabilitas kepala & ritme pendulum yang sama.',
			category: 'technique'
		});
	} else if (shotType === 'chip' || shotType === 'pitch') {
		personalized.push({
			text: 'Short game: gerakan minimal, kontrol lebih penting dari power.',
			category: 'technique'
		});
	} else if (club === 'driver') {
		personalized.push({
			text: 'Driver: rotasi lebar + smooth tempo = jarak tanpa kehilangan akurasi.',
			category: 'technique'
		});
	}

	return [...personalized, ...LOADING_TIPS];
}
