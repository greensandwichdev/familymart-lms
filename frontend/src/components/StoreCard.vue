<template>
	<div
		v-if="store.store_name"
		class="flex flex-col h-full rounded-md border-2 overflow-auto text-ink-gray-9 hover:shadow-md transition-shadow cursor-pointer"
		style="min-height: 200px"
	>
		<div
			class="w-[100%] h-[100px] bg-cover bg-center bg-no-repeat"
			:style="cardStyle"
		>
			<div
				v-if="!store.image"
				class="flex items-center justify-center text-white flex-1 font-bold my-auto px-5 text-center leading-5 h-full"
			>
				{{ store.store_name }}
			</div>
		</div>
		<div class="flex flex-col flex-auto p-4">
			<div class="flex items-center justify-between mb-2">
				<div v-if="store.member_count !== undefined">
					<Tooltip :text="__('Members')">
						<span class="flex items-center">
							<Users class="h-4 w-4 stroke-1.5 mr-1" />
							{{ store.member_count }}
						</span>
					</Tooltip>
				</div>
				<div v-if="store.is_active" class="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded">
					{{ __('Active') }}
				</div>
				<div v-else class="text-xs text-gray-500 bg-gray-50 px-2 py-0.5 rounded">
					{{ __('Inactive') }}
				</div>
			</div>

			<div class="font-semibold text-lg leading-6 mb-1">
				{{ store.store_name }}
			</div>

			<div v-if="store.store_code" class="text-sm text-ink-gray-6 mb-1">
				{{ store.store_code }}
			</div>

			<div v-if="store.organization" class="text-sm text-ink-gray-6 mb-2">
				{{ store.organization }}
			</div>

			<div class="text-sm text-ink-gray-5">
				<div v-if="store.province || store.regency || store.district">
					<MapPin class="h-3 w-3 inline mr-1" />
					{{ regionDisplay }}
				</div>
			</div>
		</div>
	</div>
</template>
<script setup>
import { MapPin, Users } from 'lucide-vue-next'
import { Tooltip } from 'frappe-ui'
import { computed } from 'vue'

const props = defineProps({
	store: {
		type: Object,
		default: null,
	},
})

const cardStyle = computed(() => {
	if (props.store?.image) {
		return { backgroundImage: `url('${encodeURI(props.store.image)}')` }
	}
	return {
		backgroundImage: getGradientColor(),
		backgroundBlendMode: 'screen',
	}
})

const regionDisplay = computed(() => {
	const parts = []
	if (props.store?.province) parts.push(props.store.province)
	if (props.store?.regency) parts.push(props.store.regency)
	if (props.store?.district) parts.push(props.store.district)
	return parts.join(' • ')
})

const getGradientColor = () => {
	const colors = ['blue', 'green', 'purple', 'orange', 'pink', 'teal']
	const colorIndex = props.store?.store_name ? props.store.store_name.charCodeAt(0) % colors.length : 0
	const color = colors[colorIndex]
	const colorValues = {
		blue: '#60a5fa',
		green: '#4ade80',
		purple: '#c084fc',
		orange: '#fb923c',
		pink: '#f472b6',
		teal: '#2dd4bf',
	}
	return `linear-gradient(to top right, #1f2937, ${colorValues[color]})`
}
</script>
