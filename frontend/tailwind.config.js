/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				obsidian: '#0B0F14',
				graphite: '#151A21',
				border: '#252C35',
				golf: '#1E7A3D',
				highlight: '#A6E3A1',
				offwhite: '#E8E8E8',
				muted: '#9AA3AD',
				disabled: '#5C6570',
				warning: '#D6A84F',
				error: '#D96C6C'
			},
			fontFamily: {
				display: ['Montserrat', 'system-ui', 'sans-serif'],
				sans: ['Inter', 'system-ui', 'sans-serif']
			},
			borderRadius: {
				sm: '4px',
				DEFAULT: '6px',
				md: '8px',
				lg: '12px',
				xl: '16px'
			}
		}
	},
	plugins: []
};
