<template>
	<div class="">
		<header
			class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
		>
			<Breadcrumbs class="h-7" :items="breadcrumbs" />
		</header>

		<div v-if="storeDetails.loading" class="p-10 text-center text-ink-gray-6">
			{{ __('Loading...') }}
		</div>

		<div v-else-if="!storeDetails.data" class="p-10 text-center text-ink-gray-6">
			{{ __('Store not found.') }}
		</div>

		<div v-else class="p-5">
			<div class="mb-6">
				<div class="text-2xl font-semibold text-ink-gray-9">
					{{ storeDetails.data.store_name }}
				</div>
				<div class="text-ink-gray-6 mt-1">
					{{ storeDetails.data.store_code }}
					<span v-if="storeDetails.data.organization"> | {{ storeDetails.data.organization }}</span>
				</div>
			</div>

			<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
				<div class="lg:col-span-2 space-y-6">
					<div class="border rounded-md p-5">
						<div class="text-lg font-semibold mb-4">{{ __('Store Information') }}</div>
						<div class="space-y-3">
							<div v-if="storeDetails.data.address" class="flex">
								<div class="w-32 text-ink-gray-5">{{ __('Address') }}</div>
								<div class="text-ink-gray-9">{{ storeDetails.data.address }}</div>
							</div>
							<div v-if="storeDetails.data.province || storeDetails.data.regency || storeDetails.data.district" class="flex">
								<div class="w-32 text-ink-gray-5">{{ __('Region') }}</div>
								<div class="text-ink-gray-9">{{ getRegionDisplay() }}</div>
							</div>
							<div class="flex">
								<div class="w-32 text-ink-gray-5">{{ __('Status') }}</div>
								<div>
									<span
										v-if="storeDetails.data.is_active"
										class="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded"
									>
										{{ __('Active') }}
									</span>
									<span
										v-else
										class="text-xs text-gray-500 bg-gray-50 px-2 py-0.5 rounded"
									>
										{{ __('Inactive') }}
									</span>
								</div>
							</div>
						</div>
					</div>

					<div class="border rounded-md p-5">
						<div class="flex items-center justify-between mb-4">
							<div class="text-lg font-semibold">{{ __('Members') }}</div>
							<Button variant="solid" @click="openAddMemberDialog">
								<template #prefix>
									<Plus class="size-4 stroke-1.5" />
								</template>
								{{ __('Add Member') }}
							</Button>
						</div>

						<div v-if="storeDetails.data.members?.length" class="overflow-x-auto">
							<table class="w-full">
								<thead class="bg-surface-gray-2">
									<tr>
										<th class="text-left p-3">{{ __('Name') }}</th>
										<th class="text-left p-3">{{ __('Email') }}</th>
										<th class="text-left p-3">{{ __('Rank') }}</th>
										<th class="text-left p-3">{{ __('Status') }}</th>
										<th class="text-right p-3">{{ __('Actions') }}</th>
									</tr>
								</thead>
								<tbody class="divide-y">
									<tr v-for="member in storeDetails.data.members" :key="member.name">
										<td class="p-3">
											<div class="flex items-center gap-2">
												<Avatar :label="member.full_name" size="sm" />
												{{ member.full_name }}
											</div>
										</td>
										<td class="p-3 text-sm text-ink-gray-6">{{ member.email }}</td>
										<td class="p-3">
											<span v-if="member.rank_name" class="text-sm bg-surface-gray-2 px-2 py-1 rounded">
												{{ member.rank_name }}
											</span>
											<span v-else class="text-sm text-ink-gray-5">-</span>
										</td>
										<td class="p-3">
											<span
												v-if="member.enabled"
												class="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded"
											>
												{{ __('Active') }}
											</span>
											<span
												v-else
												class="text-xs text-gray-500 bg-gray-50 px-2 py-0.5 rounded"
											>
												{{ __('Inactive') }}
											</span>
										</td>
										<td class="p-3 text-right">
											<Button variant="ghost" @click="editMember(member)">
												<template #prefix>
													<Pencil class="size-4 stroke-1.5" />
												</template>
											</Button>
											<Button variant="ghost" @click="confirmDeleteMember(member)">
												<template #prefix>
													<Trash2 class="size-4 stroke-1.5 text-red-500" />
												</template>
											</Button>
										</td>
									</tr>
								</tbody>
							</table>
						</div>
						<div v-else class="py-8 text-center text-ink-gray-6">
							{{ __('No members in this store.') }}
						</div>
					</div>

					<div v-if="Object.keys(storeDetails.data.program_stats || {}).length" class="border rounded-md p-5">
						<div class="text-lg font-semibold mb-4">{{ __('Program Enrollments') }}</div>
						<div class="space-y-4">
							<div
								v-for="(stats, programName) in storeDetails.data.program_stats"
								:key="programName"
								class="border rounded-md p-4"
							>
								<div class="font-medium mb-2">{{ programName }}</div>
								<div class="grid grid-cols-4 gap-4 text-sm">
									<div>
										<div class="text-ink-gray-5">{{ __('Total') }}</div>
										<div class="text-lg font-semibold">{{ stats.total }}</div>
									</div>
									<div>
										<div class="text-ink-gray-5">{{ __('Completed') }}</div>
										<div class="text-lg font-semibold text-green-600">{{ stats.completed }}</div>
									</div>
									<div>
										<div class="text-ink-gray-5">{{ __('In Progress') }}</div>
										<div class="text-lg font-semibold text-blue-600">{{ stats.in_progress }}</div>
									</div>
									<div>
										<div class="text-ink-gray-5">{{ __('Not Started') }}</div>
										<div class="text-lg font-semibold text-gray-500">{{ stats.not_started }}</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>

				<div class="space-y-6">
					<div v-if="storeDetails.data.image || true" class="border rounded-md p-5">
						<div class="flex items-center justify-between mb-4">
							<div class="text-lg font-semibold">{{ __('Store Image') }}</div>
						</div>
						<div class="space-y-3">
							<div
								class="w-full h-32 bg-cover bg-center bg-no-repeat rounded-md"
								:style="imageStyle"
							>
								<div
									v-if="!storeDetails.data.image"
									class="flex items-center justify-center text-white font-bold h-full"
								>
									{{ storeDetails.data.store_name }}
								</div>
							</div>
							<FileUploader
								:fileTypes="['image/*']"
								:validateFile="validateFile"
								@success="(file) => saveImage(file)"
							>
								<template
									v-slot="{ file, progress, uploading, openFileSelector }"
								>
									<Button @click="openFileSelector" :loading="uploading" variant="subtle" size="sm">
										{{ uploading ? `Uploading ${progress}%` : __('Change Image') }}
									</Button>
								</template>
							</FileUploader>
						</div>
					</div>

					<div class="border rounded-md p-5">
						<div class="text-lg font-semibold mb-4">{{ __('Statistics') }}</div>
						<div class="space-y-4">
							<div class="flex items-center justify-between">
								<div class="text-ink-gray-6">{{ __('Total Members') }}</div>
								<div class="text-xl font-semibold">{{ storeDetails.data.member_count }}</div>
							</div>
							<div class="flex items-center justify-between">
								<div class="text-ink-gray-6">{{ __('Total Enrollments') }}</div>
								<div class="text-xl font-semibold">{{ storeDetails.data.total_enrollments }}</div>
							</div>
							<div class="flex items-center justify-between">
								<div class="text-ink-gray-6">{{ __('Completed') }}</div>
								<div class="text-xl font-semibold text-green-600">{{ storeDetails.data.completed_enrollments }}</div>
							</div>
							<div class="flex items-center justify-between">
								<div class="text-ink-gray-6">{{ __('In Progress') }}</div>
								<div class="text-xl font-semibold text-blue-600">{{ storeDetails.data.in_progress_enrollments }}</div>
							</div>
						</div>
					</div>

					<div v-if="Object.keys(storeDetails.data.member_stats || {}).length" class="border rounded-md p-5">
						<div class="text-lg font-semibold mb-4">{{ __('Members by Rank') }}</div>
						<DonutChart
							v-if="memberChartData"
							:config="memberChartData"
						/>
					</div>

					<div v-if="storeDetails.data.total_enrollments" class="border rounded-md p-5">
						<div class="text-lg font-semibold mb-4">{{ __('Enrollment Progress') }}</div>
						<DonutChart
							v-if="enrollmentChartData"
							:config="enrollmentChartData"
						/>
					</div>
				</div>
			</div>
		</div>

		<Dialog
			v-model="showMemberDialog"
			:options="{
				title: editingMember ? __('Edit Member') : __('Add Member'),
				size: 'lg',
				actions: [
					{
						label: editingMember ? __('Update') : __('Add'),
						variant: 'solid',
						onClick: ({ close }) => saveMember(close),
					},
				],
			}"
		>
			<template #body-content>
				<div class="space-y-4">
					<FormControl
						v-if="!editingMember"
						v-model="memberForm.email"
						:label="__('Email')"
						placeholder="user@example.com"
						type="email"
						class="w-full"
						:required="true"
					/>
					<div v-else class="space-y-4">
						<FormControl
							v-model="memberForm.email"
							:label="__('Email')"
							type="email"
							class="w-full"
							:disabled="true"
						/>
						<FormControl
							v-model="memberForm.full_name"
							:label="__('Full Name')"
							type="text"
							class="w-full"
						/>
					</div>
					<Link
						class="w-full"
						v-model="memberForm.store_rank"
						doctype="Store Rank"
						:label="__('Store Rank')"
						placeholder="Select rank"
					/>
				</div>
			</template>
		</Dialog>

		<Dialog
			v-model="showDeleteDialog"
			:options="{
				title: __('Remove Member'),
				size: 'sm',
				actions: [
					{
						label: __('Remove'),
						variant: 'solid',
						theme: 'red',
						onClick: ({ close }) => deleteMember(close),
					},
				],
			}"
		>
			<template #body-content>
				<p class="text-ink-gray-6">
					{{ __('Are you sure you want to remove this member from the store?') }}
				</p>
				<p v-if="deletingMember" class="mt-2 font-medium text-ink-gray-9">
					{{ deletingMember.full_name }} ({{ deletingMember.email }})
				</p>
			</template>
		</Dialog>
	</div>
</template>
<script setup>
import {
	Avatar,
	Button,
	Breadcrumbs,
	Dialog,
	DonutChart,
	FileUploader,
	FormControl,
	createResource,
} from 'frappe-ui'
import { ref, computed } from 'vue'
import { Plus, Pencil, Trash2 } from 'lucide-vue-next'
import Link from '@/components/Controls/Link.vue'

const props = defineProps({
	storeName: {
		type: String,
		required: true,
	},
})

const showMemberDialog = ref(false)
const showDeleteDialog = ref(false)
const editingMember = ref(null)
const deletingMember = ref(null)

const memberForm = ref({
	email: '',
	full_name: '',
	store_rank: '',
})

const storeDetails = createResource({
	url: 'lms.lms.store.get_store_details',
	cache: ['storeDetails', props.storeName],
	makeParams() {
		return {
			store: props.storeName,
		}
	},
	auto: true,
})

const breadcrumbs = computed(() => [
	{
		label: __('Stores'),
		route: '/stores',
	},
	{
		label: storeDetails.data?.store_name || props.storeName,
	},
])

const memberChartData = computed(() => {
	if (!storeDetails.data?.member_stats) return null
	const stats = storeDetails.data.member_stats
	const labels = Object.keys(stats)
	const values = Object.values(stats)

	if (!labels.length) return null

	return {
		data: labels.map((label, idx) => ({
			label: label,
			value: values[idx],
		})),
		title: __('Members by Rank'),
		subtitle: '',
		categoryColumn: 'label',
		valueColumn: 'value',
	}
})

const enrollmentChartData = computed(() => {
	if (!storeDetails.data?.total_enrollments) return null

	return {
		data: [
			{ label: __('Completed'), value: storeDetails.data.completed_enrollments },
			{ label: __('In Progress'), value: storeDetails.data.in_progress_enrollments },
			{ label: __('Not Started'), value: storeDetails.data.not_started_enrollments },
		],
		title: __('Progress'),
		subtitle: '',
		categoryColumn: 'label',
		valueColumn: 'value',
	}
})

const imageStyle = computed(() => {
	if (storeDetails.data?.image) {
		return { backgroundImage: `url('${encodeURI(storeDetails.data.image)}')` }
	}
	return { backgroundImage: getGradientColor() }
})

const getGradientColor = () => {
	const colors = ['blue', 'green', 'purple', 'orange', 'pink', 'teal']
	const storeName = storeDetails.data?.store_name || ''
	const colorIndex = storeName ? storeName.charCodeAt(0) % colors.length : 0
	const colorValues = {
		blue: '#60a5fa',
		green: '#4ade80',
		purple: '#c084fc',
		orange: '#fb923c',
		pink: '#f472b6',
		teal: '#2dd4bf',
	}
	return `linear-gradient(to top right, #1f2937, ${colorValues[colors[colorIndex]]})`
}

const validateFile = (file) => {
	const extension = file.name.split('.').pop().toLowerCase()
	if (!['jpg', 'jpeg', 'png'].includes(extension)) {
		return 'Only image file is allowed.'
	}
}

const saveImage = (file) => {
	updateStoreImage.submit({
		store: props.storeName,
		data: JSON.stringify({
			image: file.file_url,
		}),
	})
}

const updateStoreImage = createResource({
	url: 'lms.lms.store.update_store',
	onSuccess() {
		storeDetails.reload()
	},
	onError(error) {
		console.error('Error updating store image:', error)
	},
})

const getRegionDisplay = () => {
	if (!storeDetails.data) return ''
	const parts = []
	if (storeDetails.data.province) parts.push(storeDetails.data.province)
	if (storeDetails.data.regency) parts.push(storeDetails.data.regency)
	if (storeDetails.data.district) parts.push(storeDetails.data.district)
	return parts.join(' • ')
}

const assignMember = createResource({
	url: 'lms.lms.store.assign_member_to_store',
	makeParams() {
		return {
			member: memberForm.value.email,
			store: props.storeName,
			rank: memberForm.value.store_rank || null,
			full_name: memberForm.value.full_name || null,
		}
	},
	auto: false,
	onSuccess() {
		showMemberDialog.value = false
		resetForm()
		storeDetails.reload()
	},
})

const updateMember = createResource({
	url: 'lms.lms.store.update_member_rank',
	makeParams() {
		return {
			member: memberForm.value.email,
			store: props.storeName,
			rank: memberForm.value.store_rank || null,
			full_name: memberForm.value.full_name,
		}
	},
	auto: false,
	onSuccess() {
		showMemberDialog.value = false
		resetForm()
		storeDetails.reload()
	},
})

const removeMember = createResource({
	url: 'lms.lms.store.remove_member_from_store',
	makeParams() {
		return {
			member: deletingMember.value?.name,
		}
	},
	auto: false,
	onSuccess() {
		showDeleteDialog.value = false
		deletingMember.value = null
		storeDetails.reload()
	},
})

const openAddMemberDialog = () => {
	editingMember.value = null
	resetForm()
	showMemberDialog.value = true
}

const editMember = (member) => {
	editingMember.value = member
	memberForm.value = {
		email: member.email,
		full_name: member.full_name,
		store_rank: member.store_rank || '',
	}
	showMemberDialog.value = true
}

const confirmDeleteMember = (member) => {
	deletingMember.value = member
	showDeleteDialog.value = true
}

const saveMember = async () => {
	try {
		if (editingMember.value) {
			await updateMember.submit()
		} else {
			await assignMember.submit()
		}
	} catch (error) {
		console.error('Error saving member:', error)
	}
}

const deleteMember = async () => {
	try {
		await removeMember.submit()
	} catch (error) {
		console.error('Error deleting member:', error)
	}
}

const resetForm = () => {
	memberForm.value = {
		email: '',
		full_name: '',
		store_rank: '',
	}
	editingMember.value = null
}
</script>
