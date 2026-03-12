<template>
	<header
		class="sticky top-0 z-10 flex flex-col md:flex-row md:items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
	>
		<Breadcrumbs :items="breadbrumbs" />
		<Button variant="solid" @click="saveProgram()">
			{{ __('Save') }}
		</Button>
	</header>
	<div v-if="program.doc" class="pt-5 px-5 w-3/4 mx-auto space-y-10">
		<FormControl v-model="program.doc.title" :label="__('Title')" />

		<!-- Courses -->
		<div>
			<div class="flex items-center justify-between mb-2">
				<div class="text-lg text-ink-gray-9 font-semibold">
					{{ __('Program Courses') }}
				</div>
				<Button
					@click="
						() => {
							currentForm = 'course'
							showDialog = true
						}
					"
				>
					<template #prefix>
						<Plus class="w-4 h-4" />
					</template>
					{{ __('Add') }}
				</Button>
			</div>

			<ListView
				:columns="courseColumns"
				:rows="program.doc.program_courses"
				row-key="name"
				:options="{
					showTooltip: false,
				}"
			>
				<ListHeader
					class="mb-2 grid items-center space-x-4 rounded bg-surface-gray-2 p-2"
				>
					<ListHeaderItem :item="item" v-for="item in courseColumns" />
				</ListHeader>
				<ListRows>
					<Draggable
						:list="program.doc.program_courses"
						item-key="name"
						group="items"
						@end="updateOrder"
						class="cursor-move"
					>
						<template #item="{ element: row }">
							<ListRow :row="row" />
						</template>
					</Draggable>
				</ListRows>
				<ListSelectBanner>
					<template #actions="{ unselectAll, selections }">
						<div class="flex gap-2">
							<Button
								variant="ghost"
								@click="remove(selections, unselectAll, 'program_courses')"
							>
								<Trash2 class="h-4 w-4 stroke-1.5" />
							</Button>
						</div>
					</template>
				</ListSelectBanner>
			</ListView>
		</div>

		<!-- Members -->
		<div>
			<div class="flex items-center justify-between mb-2">
				<div class="text-lg text-ink-gray-9 font-semibold">
					{{ __('Program Members') }}
				</div>
				<Button
					@click="
						() => {
							currentForm = 'member'
							showDialog = true
						}
					"
				>
					<template #prefix>
						<Plus class="w-4 h-4" />
					</template>
					{{ __('Add') }}
				</Button>
			</div>
		</div>

		<!-- Program Ranks Section -->
		<div class="mb-8">
			<div class="flex items-center justify-between mb-2">
				<div class="text-lg text-ink-gray-9 font-semibold">
					{{ __('Program Ranks') }}
				</div>
			</div>

			<ListView
				:columns="rankColumns"
				:rows="rankWithCounts"
				:row-key="(row) => row.name"
				:options="{
					showTooltip: false,
				}"
			>
				<ListHeader
					class="mb-2 grid items-center space-x-4 rounded bg-surface-gray-2 p-2"
				>
					<ListHeaderItem :item="item" v-for="item in rankColumns" />
				</ListHeader>
				<ListRows>
					<ListRow :row="row" v-for="row in rankWithCounts" />
				</ListRows>
				<ListSelectBanner>
					<template #actions="{ unselectAll, selections }">
						<div class="flex gap-2">
							<Button
								variant="ghost"
								@click="removeByRank(selections, unselectAll)"
							>
								<Trash2 class="h-4 w-4 stroke-1.5" />
							</Button>
						</div>
					</template>
				</ListSelectBanner>
			</ListView>
		</div>

		<!-- Members by Selection Section -->
		<div>
			<div class="flex items-center justify-between mb-2">
				<div class="text-lg text-ink-gray-9 font-semibold">
					{{ __('Members by Selection') }}
				</div>
			</div>

			<ListView
				:columns="memberDirectColumns"
				:rows="membersByMember"
				row-key="name"
				:options="{
					showTooltip: false,
				}"
			>
				<ListHeader
					class="mb-2 grid items-center space-x-4 rounded bg-surface-gray-2 p-2"
				>
					<ListHeaderItem :item="item" v-for="item in memberDirectColumns" />
				</ListHeader>
				<ListRows>
					<ListRow :row="row" v-for="row in membersByMember" />
				</ListRows>
				<ListSelectBanner>
					<template #actions="{ unselectAll, selections }">
						<div class="flex gap-2">
							<Button
								variant="ghost"
								@click="removeByMember(selections, unselectAll)"
							>
								<Trash2 class="h-4 w-4 stroke-1.5" />
							</Button>
						</div>
					</template>
				</ListSelectBanner>
			</ListView>
		</div>
	</div>

	<Dialog
		v-model="showDialog"
		:options="{
			title:
				currentForm == 'course'
					? __('New Program Course')
					: __('New Program Member'),
			actions: [
				{
					label: __('Add'),
					variant: 'solid',
					onClick: () =>
						currentForm == 'course'
							? addProgramCourse(close)
							: addProgramMember(close),
				},
			],
		}"
	>
		<template #body-content>
			<Link
				v-if="currentForm == 'course'"
				v-model="course"
				doctype="LMS Course"
				:filters="{
					disable_self_learning: 1,
				}"
				:label="__('Program Course')"
				:description="
					__(
						'Only courses for which self learning is disabled can be added to program.',
					)
				"
			/>

			<div v-if="currentForm == 'member'">
				<div class="mb-4">
					<label class="text-sm font-medium text-ink-gray-7 block mb-2">
						{{ __('Enrollment Method') }}
					</label>
					<div class="flex gap-4">
						<label class="flex items-center cursor-pointer">
							<input
								type="radio"
								v-model="enrollmentType"
								value="by_store_rank"
								class="mr-2"
							/>
							<span class="text-sm">{{ __('By Store Rank') }}</span>
						</label>
						<label class="flex items-center cursor-pointer">
							<input
								type="radio"
								v-model="enrollmentType"
								value="by_member"
								class="mr-2"
							/>
							<span class="text-sm">{{ __('By Member Selection') }}</span>
						</label>
					</div>
				</div>

				<Link
					v-if="enrollmentType === 'by_store_rank'"
					v-model="member"
					doctype="Store Rank"
					:label="__('Store Rank')"
					:onCreate="(value, close) => openSettings('Members', close)"
				/>

				<div v-if="enrollmentType === 'by_store_rank'" class="space-y-4 mt-4">
					<FormControl
						v-model="regionFilters.province"
						:label="__('Province')"
						type="select"
						:options="provinceOptions"
						placeholder="All Provinces"
						@change="onProvinceChange"
					/>
					<FormControl
						v-model="regionFilters.regency"
						:label="__('Regency')"
						type="select"
						:options="regencyOptions"
						placeholder="All Regencies"
						:disabled="!regionFilters.province"
						@change="onRegencyChange"
					/>
					<FormControl
						v-model="regionFilters.district"
						:label="__('District')"
						type="select"
						:options="districtOptions"
						placeholder="All Districts"
						:disabled="!regionFilters.regency"
					/>
				</div>

				<MultiSelect
					v-if="enrollmentType === 'by_member'"
					v-model="selectedMembers"
					doctype="User"
					:label="__('Select Members')"
				/>
			</div>
		</template>
	</Dialog>
</template>
<script setup>
import {
	Breadcrumbs,
	Button,
	call,
	createDocumentResource,
	Dialog,
	FormControl,
	ListView,
	ListRows,
	ListRow,
	ListHeader,
	ListHeaderItem,
	ListSelectBanner,
	usePageMeta,
	toast,
} from 'frappe-ui'
import { computed, ref, watch } from 'vue'
import { Plus, Trash2 } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { sessionStore } from '@/stores/session'
import { openSettings } from '@/utils'
import Draggable from 'vuedraggable'
import Link from '@/components/Controls/Link.vue'
import MultiSelect from '@/components/Controls/MultiSelect.vue'

const { brand } = sessionStore()
const showDialog = ref(false)
const currentForm = ref(null)
const course = ref(null)
const member = ref(null)
const enrollmentType = ref('by_store_rank')
const selectedMembers = ref([])
const router = useRouter()

const regionFilters = ref({
	province: '',
	regency: '',
	district: '',
})

const provinceOptions = ref([])
const regencyOptions = ref([])
const districtOptions = ref([])

const props = defineProps({
	programName: {
		type: String,
		required: true,
	},
})

// Fetch provinces on mount
call('lms.lms.store.get_provinces').then((data) => {
	provinceOptions.value = [{ label: 'All Provinces', value: '' }, ...data.map(p => ({ label: p.name, value: p.name }))]
})

const onProvinceChange = async () => {
	regionFilters.value.regency = ''
	regionFilters.value.district = ''
	regencyOptions.value = []
	districtOptions.value = []
	
	if (regionFilters.value.province) {
		const data = await call('lms.lms.store.get_regencies', { province: regionFilters.value.province })
		regencyOptions.value = [{ label: 'All Regencies', value: '' }, ...data.map(r => ({ label: r.name, value: r.name }))]
	}
}

const onRegencyChange = async () => {
	regionFilters.value.district = ''
	districtOptions.value = []
	
	if (regionFilters.value.regency) {
		const data = await call('lms.lms.store.get_districts', { regency: regionFilters.value.regency })
		districtOptions.value = [{ label: 'All Districts', value: '' }, ...data.map(d => ({ label: d.name, value: d.name }))]
	}
}

const rankCache = ref({})

const program = createDocumentResource({
	doctype: 'LMS Program',
	name: props.programName,
	auto: true,
	cache: ['program', props.programName],
})

watch(
	() => program.doc?.program_members,
	async (members) => {
		if (!members) return

		const missingRanks = [
			...new Set(
				members
					.filter((m) => m.store_rank && !rankCache.value[m.store_rank])
					.map((m) => m.store_rank),
			),
		]

		if (missingRanks.length) {
			try {
				const res = await call('frappe.client.get_list', {
					doctype: 'Store Rank',
					filters: [['name', 'in', missingRanks]],
					fields: ['name', 'rank_name'],
				})

				res.forEach((r) => {
					rankCache.value[r.name] = r.rank_name
				})
			} catch (err) {
				console.error('Failed to fetch ranks', err)
			}
		}

		members.forEach((m) => {
			if (m.store_rank) {
				m.store_rank_name = rankCache.value[m.store_rank] || m.store_rank
			}
		})
	},
	{ deep: true, immediate: true },
)

// Computed properties to separate members by enrollment type
const membersByRank = computed(() => {
	return (program.doc?.program_members || []).filter((m) => m.store_rank)
})

const membersByMember = computed(() => {
	return (program.doc?.program_members || []).filter((m) => !m.store_rank)
})

// Program ranks - configured ranks for the program
const programRanks = computed(() => {
	return program.doc?.program_ranks || []
})

// Compute member count for each program rank
const rankWithCounts = computed(() => {
	const membersByRankMap = {}
	;(program.doc?.program_members || []).forEach((m) => {
		if (m.store_rank) {
			if (!membersByRankMap[m.store_rank]) {
				membersByRankMap[m.store_rank] = 0
			}
			membersByRankMap[m.store_rank]++
		}
	})
	
	return (program.doc?.program_ranks || []).map((r) => ({
		name: r.name,
		store_rank: r.store_rank,
		rank_name: r.rank_name || r.store_rank,
		province: r.province || '',
		regency: r.regency || '',
		district: r.district || '',
		count: membersByRankMap[r.store_rank] || 0,
	}))
})

const rankColumns = [
	{ label: 'Store Rank', key: 'rank_name', width: '30%' },
	{ label: 'Province', key: 'province', width: '20%' },
	{ label: 'Regency', key: 'regency', width: '20%' },
	{ label: 'District', key: 'district', width: '20%' },
	{ label: 'Members', key: 'count', width: '10%' },
]

const memberDirectColumns = [
	{ label: 'Full Name', key: 'full_name', width: '40%' },
	{ label: 'Email', key: 'email', width: '40%' },
	{ label: 'Progress (%)', key: 'progress', width: '20%' },
]

const addProgramCourse = () => {
	program.setValue.submit(
		{
			program_courses: [
				...program.doc.program_courses,
				{ course: course.value },
			],
		},
		{
			onSuccess(data) {
				showDialog.value = false
				course.value = null
				toast.success(__('Course added to program'))
				program.reload()
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		},
	)
}

const addProgramMember = async () => {
	try {
		if (enrollmentType.value === 'by_store_rank') {
			// Method 1: By Store Rank - Add to program_ranks (rank configuration)
			if (!member.value) {
				toast.error(__('Please select a Store Rank'))
				return
			}

			// Check if this rank already exists in program_ranks
			const existingRanks = program.doc?.program_ranks || []
			const rankExists = existingRanks.some(
				(r) => r.store_rank === member.value &&
					(r.province || '') === (regionFilters.value.province || '') &&
					(r.regency || '') === (regionFilters.value.regency || '') &&
					(r.district || '') === (regionFilters.value.district || '')
			)

			if (rankExists) {
				toast.error(__('This rank with the same region filters already exists'))
				return
			}

			// Add to program_ranks
			const newRank = {
				store_rank: member.value,
				province: regionFilters.value.province || '',
				regency: regionFilters.value.regency || '',
				district: regionFilters.value.district || '',
			}

			program.setValue.submit(
				{
					program_ranks: [...existingRanks, newRank],
				},
				{
					onSuccess: async (data) => {
						// Sync members based on new rank config
						try {
							await call('lms.lms.api.sync_program_members_by_ranks', {
								program: props.programName,
							})
						} catch (e) {
							console.error('Failed to sync members:', e)
						}

						showDialog.value = false
						member.value = null
						regionFilters.value = { province: '', regency: '', district: '' }
						regencyOptions.value = []
						districtOptions.value = []
						toast.success(__('Rank added to program'))
						program.reload()
					},
					onError(err) {
						toast.error(err.messages?.[0] || err)
					},
				},
			)
			return
		}

		// Method 2: By Member Selection - Add to program_members directly
		let memberList = []

		if (!selectedMembers.value || selectedMembers.value.length === 0) {
			toast.error(__('Please select at least one member'))
			return
		}

		// Fetch user details for each selected user
		for (const userName of selectedMembers.value) {
			try {
				const userDetails = await call('frappe.client.get', {
					doctype: 'User',
					name: userName,
				})
				memberList.push({
					member: userName,
					store_rank: null,
					full_name: userDetails.full_name,
					email: userDetails.email,
				})
			} catch (err) {
				console.error('Failed to fetch user details for:', userName, err)
			}
		}

		// Filter out duplicates
		const existingMembers = program.doc.program_members || []
		const existingMemberNames = new Set(existingMembers.map((m) => m.member))
		const newMembers = memberList.filter((m) => !existingMemberNames.has(m.member))

		if (newMembers.length === 0) {
			toast.error(__('All selected members are already in the program'))
			return
		}

		const updatedMembers = [...existingMembers, ...newMembers]

		program.setValue.submit(
			{
				program_members: updatedMembers,
			},
			{
				onSuccess(data) {
					showDialog.value = false
					member.value = null
					selectedMembers.value = []
					enrollmentType.value = 'by_store_rank'
					regionFilters.value = { province: '', regency: '', district: '' }
					regencyOptions.value = []
					districtOptions.value = []
					toast.success(__('Member(s) added to program'))
					program.reload()
				},
				onError(err) {
					toast.error(err.messages?.[0] || err)
				},
			},
		)
	} catch (err) {
		console.error(err)
		toast.error(__('Failed to add members'))
	}
}

const remove = (selections, unselectAll, doctype) => {
	selections = Array.from(selections)
	program.setValue.submit(
		{
			[doctype]: program.doc[doctype].filter(
				(row) => !selections.includes(row.name),
			),
		},
		{
			onSuccess(data) {
				unselectAll()
				toast.success(__('Items removed successfully'))
				program.reload()
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		},
	)
}

const removeByRank = (selections, unselectAll) => {
	selections = Array.from(selections)
	const ranksToRemove = selections.map((r) => r.store_rank)

	// Remove from program_ranks
	const updatedRanks = (program.doc.program_ranks || []).filter(
		(row) => !ranksToRemove.includes(row.store_rank),
	)

	// For program_members: keep members with progress > 1%, remove those with 0%
	const existingMembers = program.doc.program_members || []
	const updatedMembers = existingMembers.map((m) => {
		if (ranksToRemove.includes(m.store_rank)) {
			if (m.progress > 1) {
				// Keep member but clear store_rank (becomes manual)
				return { ...m, store_rank: null }
			}
			// Remove member with 0% progress
			return null
		}
		return m
	}).filter(Boolean)

	program.setValue.submit(
		{
			program_ranks: updatedRanks,
			program_members: updatedMembers,
		},
		{
			onSuccess(data) {
				unselectAll()
				toast.success(__('Rank removed from program'))
				program.reload()
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		},
	)
}

const removeByMember = (selections, unselectAll) => {
	selections = Array.from(selections)
	const membersToRemove = new Set(selections.map((r) => r.name))
	
	const updatedMembers = (program.doc.program_members || []).filter(
		(row) => !membersToRemove.has(row.name),
	)
	
	program.setValue.submit(
		{
			program_members: updatedMembers,
		},
		{
			onSuccess(data) {
				unselectAll()
				toast.success(__('Members removed successfully'))
				program.reload()
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		},
	)
}

const updateOrder = (e) => {
	let sourceIdx = e.from.dataset.idx
	let targetIdx = e.to.dataset.idx
	let courses = program.doc.program_courses
	courses.splice(targetIdx, 0, courses.splice(sourceIdx, 1)[0])

	courses.forEach((course, index) => {
		course.idx = index + 1
	})

	program.setValue.submit(
		{
			program_courses: courses,
		},
		{
			onSuccess(data) {
				toast.success(__('Course moved successfully'))
				program.reload()
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		},
	)
}

const saveProgram = () => {
	call('frappe.model.rename_doc.update_document_title', {
		doctype: 'LMS Program',
		docname: program.doc.name,
		name: program.doc.title,
	}).then((data) => {
		router.push({ name: 'ProgramForm', params: { programName: data } })
	})
}

const courseColumns = computed(() => {
	return [
		{
			label: 'Title',
			key: 'course_title',
			width: 3,
		},
		{
			label: 'ID',
			key: 'course',
			width: 3,
		},
	]
})

const memberColumns = computed(() => {
	return [
		{
			label: 'Member',
			key: 'member',
			width: 3,
			align: 'left',
		},
		{
			label: 'Store Rank',
			key: 'store_rank_name',
			width: 3,
			align: 'left',
		},
		{
			label: 'Full Name',
			key: 'full_name',
			width: 3,
			align: 'left',
		},
		{
			label: 'Progress (%)',
			key: 'progress',
			width: 3,
			align: 'right',
		},
	]
})

const breadbrumbs = computed(() => {
	return [
		{
			label: 'Programs',
			route: { name: 'Programs' },
		},
		{
			label: props.programName === 'new' ? 'New Program' : props.programName,
		},
	]
})

usePageMeta(() => {
	return {
		title: program.doc?.title,
		icon: brand.favicon,
	}
})
</script>
