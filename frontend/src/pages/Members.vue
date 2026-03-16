<template>
	<div class="">
		<header
			class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
		>
			<Breadcrumbs class="h-7" :items="breadcrumbs" />
		</header>
		<div class="p-5">
			<div class="mb-6">
				<div class="text-2xl font-semibold text-ink-gray-9">
					{{ __('Members') }}
				</div>
				<div class="text-ink-gray-6 mt-1">
					{{ __('View and manage members across all stores') }}
				</div>
			</div>

			<div class="mb-4 flex items-center justify-between">
				<FormControl
					v-model="search"
					:placeholder="__('Search')"
					type="text"
					:debounce="300"
					class="w-64"
				>
					<template #prefix>
						<Search class="size-4 stroke-1.5 text-ink-gray-5" />
					</template>
				</FormControl>
				<Button variant="solid" @click="openNewMemberDialog">
					<template #prefix>
						<Plus class="size-4 stroke-1.5" />
					</template>
					{{ __('New Member') }}
				</Button>
			</div>

			<ListView
				v-if="memberList.length"
				:columns="memberColumns"
				:rows="memberList"
				row-key="name"
				:options="{ showTooltip: false, selectable: false }"
			>
				<ListHeader class="mb-2 grid items-center space-x-4 rounded bg-surface-gray-2 p-2">
					<ListHeaderItem :item="item" v-for="item in memberColumns" />
				</ListHeader>
				<ListRows>
					<ListRow
						v-for="row in memberList"
						:row="row"
					>
						<template #default="{ column }">
							<ListRowItem :item="row[column.key]" :align="column.align">
								<div v-if="column.key === 'full_name'">
									<div class="flex items-center gap-3">
										<Avatar
											:image="row.user_image"
											:label="row.full_name"
											size="sm"
										/>
										<div>
											<div class="font-medium text-ink-gray-9">{{ row.full_name }}</div>
										</div>
									</div>
								</div>
								<div v-else-if="column.key === 'name'">
									<div class="text-sm text-ink-gray-7">{{ row.name }}</div>
								</div>
								<div v-else-if="column.key === 'store_rank_name'">
									<div class="text-sm text-ink-gray-7">{{ row.store_rank_name || '-' }}</div>
								</div>
								<div v-else-if="column.key === 'lms_store_name'">
									<div class="text-sm text-ink-gray-7">{{ row.lms_store_name || '-' }}</div>
								</div>
								<div v-else-if="column.key === 'region_display'">
									<div class="text-sm text-ink-gray-7">{{ row.region_display || '-' }}</div>
								</div>
								<div v-else-if="column.key === 'role'">
									<div
										v-if="row.role && row.role !== 'LMS Student'"
										class="flex items-center gap-1 bg-surface-gray-2 px-2 py-1 rounded-md text-sm"
									>
										<Shield class="size-3 stroke-1.5" />
										{{ getRole(row.role) }}
									</div>
									<div v-else class="text-sm text-ink-gray-5">-</div>
								</div>
								<div v-else-if="column.key === 'actions'">
									<div class="flex items-center gap-1">
										<Button variant="ghost" @click.stop="editMember(row)">
											<template #prefix>
												<Pencil class="size-4 stroke-1.5" />
											</template>
										</Button>
										<Button variant="ghost" @click.stop="confirmDelete(row)">
											<template #prefix>
												<Trash2 class="size-4 stroke-1.5 text-red-500" />
											</template>
										</Button>
									</div>
								</div>
								<div v-else>
									{{ row[column.key] }}
								</div>
							</ListRowItem>
						</template>
					</ListRow>
				</ListRows>
			</ListView>
			<div v-else-if="members.loading" class="py-10 text-center text-ink-gray-6">
				{{ __('Loading...') }}
			</div>
			<div v-else class="py-10 text-center text-ink-gray-6">
				{{ __('No members found.') }}
			</div>

			<div
				v-if="memberList.length && hasNextPage"
				class="mt-4 flex justify-center"
			>
				<Button @click="members.reload()">
					<template #prefix>
						<RefreshCw class="h-3 w-3 stroke-1.5" />
					</template>
					{{ __('Load More') }}
				</Button>
			</div>
		</div>

		<!-- New/Edit Member Dialog -->
		<Dialog
			v-model="showMemberDialog"
			:options="{
				title: editingMember ? __('Edit Member') : __('New Member'),
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
						v-model="memberForm.email"
						:label="__('Email')"
						placeholder="user@example.com"
						type="email"
						class="w-full"
						:required="true"
						:disabled="!!editingMember"
					/>
					<FormControl
						v-model="memberForm.full_name"
						:label="__('Full Name')"
						placeholder="John"
						type="text"
						class="w-full"
						:required="true"
					/>
					<FormControl
						class="w-full"
						v-model="memberForm.lms_store"
						type="select"
						:options="storeOptions"
						:disabled="userResource.data?.is_store_manager"
						:label="__('Store')"
						placeholder="Select store"
					/>
					<FormControl
						class="w-full"
						v-model="memberForm.store_rank"
						type="select"
						:options="rankOptions"
						:label="__('Store Rank')"
						placeholder="Select rank"
					/>
					<FormControl
						v-model="memberForm.role"
						:label="__('Role')"
						type="select"
						:options="roleOptions"
						class="w-full"
					/>
				</div>
			</template>
		</Dialog>

		<!-- Delete Confirmation Dialog -->
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
					{{ __('Are you sure you want to remove this member from their store?') }}
				</p>
				<p v-if="deletingMember" class="mt-2 font-medium text-ink-gray-9">
					{{ deletingMember.full_name }} ({{ deletingMember.name }})
				</p>
			</template>
		</Dialog>
	</div>
</template>
<script setup lang="ts">
import {
	Avatar,
	Button,
	Breadcrumbs,
	ListView,
	ListHeader,
	ListHeaderItem,
	ListRows,
	ListRow,
	ListRowItem,
	Dialog,
	FormControl,
	createResource,
	toast,
} from 'frappe-ui'
import { useRouter } from 'vue-router'
import { ref, watch, computed, onMounted } from 'vue'
import { RefreshCw, Search, Shield, Plus, Pencil, Trash2 } from 'lucide-vue-next'
import Link from '@/components/Controls/Link.vue'
import { usersStore } from '@/stores/user'

const router = useRouter()
const { userResource } = usersStore()

// Fetch stores based on user access
const stores = createResource({
	url: 'lms.lms.store.get_stores',
	auto: true,
})

// Fetch store ranks
const ranks = createResource({
	url: 'lms.lms.store.get_store_ranks',
	auto: true,
})

// Store options computed property
const storeOptions = computed(() => {
	if (!stores.data) return []
	
	// If Store Manager, return only their own store (disabled)
	if (userResource.data?.is_store_manager && userResource.data?.lms_store) {
		const myStore = stores.data.find(s => s.name === userResource.data.lms_store)
		if (myStore) {
			return [{
				label: myStore.store_name,
				value: myStore.name,
				disabled: true
			}]
		}
	}
	
	// Otherwise return all accessible stores
	return stores.data.map(store => ({
		label: store.store_name,
		value: store.name,
	}))
})

// Rank options computed property
const rankOptions = computed(() => {
	if (!ranks.data) return []
	return ranks.data.map(rank => ({
		label: rank.rank_name,
		value: rank.name,
	}))
})

// Route guard - redirect if no access
onMounted(() => {
	const checkAccess = () => {
		if (!userResource.data) return
		
		const roles = userResource.data.roles?.map(r => r.role) || []
		const isBrandAdmin = userResource.data.is_brand_admin
		const isStoreManager = userResource.data.is_store_manager
		const isSystemManager = userResource.data.is_system_manager
		
		const effectiveRoles = [...roles]
		if (isBrandAdmin) effectiveRoles.push('Brand Admin')
		if (isStoreManager) effectiveRoles.push('Store Manager')
		if (isSystemManager) effectiveRoles.push('System Manager')
		
		const requiredRoles = ['Brand Admin', 'Store Manager', 'System Manager']
		const hasAccess = requiredRoles.some(role => effectiveRoles.includes(role))
		
		if (!hasAccess) {
			router.push('/')
		}
	}
	
	if (userResource.data) {
		checkAccess()
	} else {
		// Wait for userResource to load
		const unwatch = watch(() => userResource.data, () => {
			unwatch()
			checkAccess()
		})
	}
})

const breadcrumbs = computed(() => [
	{
		label: __('Members'),
		route: '/members',
	},
])

const memberColumns = computed(() => [
	{
		label: __('Name'),
		key: 'full_name',
		width: 2,
	},
	{
		label: __('Email'),
		key: 'name',
		width: 2,
	},
	{
		label: __('Rank'),
		key: 'store_rank_name',
		width: 1,
	},
	{
		label: __('Store'),
		key: 'lms_store_name',
		width: 1,
	},
	{
		label: __('Region'),
		key: 'region_display',
		width: 1,
	},
	{
		label: __('Role'),
		key: 'role',
		width: 1,
	},
	{
		label: __('Actions'),
		key: 'actions',
		width: 1,
		align: 'right',
	},
])

const search = ref('')
const start = ref(0)
const memberList = ref<Member[]>([])
const hasNextPage = ref(false)
const showMemberDialog = ref(false)
const showDeleteDialog = ref(false)
const editingMember = ref<Member | null>(null)
const deletingMember = ref<Member | null>(null)

const memberForm = ref({
	email: '',
	full_name: '',
	lms_store: '',
	store_rank: '',
	role: '',
})

const roleOptions = [
	{ label: __('No Role'), value: '' },
	{ label: __('Moderator'), value: 'Moderator' },
	{ label: __('Brand Admin'), value: 'Brand Admin' },
	{ label: __('Store Manager'), value: 'Store Manager' },
	{ label: __('Course Creator'), value: 'Course Creator' },
	{ label: __('Batch Evaluator'), value: 'Batch Evaluator' },
	{ label: __('LMS Student'), value: 'LMS Student' },
]

const members = createResource({
	url: 'lms.lms.api.get_members',
	makeParams: () => {
		return {
			search: search.value,
			start: start.value,
		}
	},
	onSuccess(data: Member[]) {
		memberList.value = memberList.value.concat(data)
		start.value = start.value + 20
		hasNextPage.value = data.length === 20
	},
	auto: true,
})

const createMember = createResource({
	url: 'lms.lms.store.create_member',
	makeParams() {
		return {
			email: memberForm.value.email,
			full_name: memberForm.value.full_name,
			lms_store: memberForm.value.lms_store || null,
			store_rank: memberForm.value.store_rank || null,
			role: memberForm.value.role || null,
		}
	},
	auto: false,
	onSuccess() {
		showMemberDialog.value = false
		resetForm()
		reloadMembers()
	},
	onError(error) {
		console.error('Error creating member:', error)
	},
})

const assignMember = createResource({
	url: 'lms.lms.store.assign_member_to_store',
	makeParams() {
		return {
			member: memberForm.value.email,
			store: memberForm.value.lms_store,
			rank: memberForm.value.store_rank,
			full_name: memberForm.value.full_name,
		}
	},
	auto: false,
	onSuccess() {
		showMemberDialog.value = false
		resetForm()
		reloadMembers()
	},
})

const updateMember = createResource({
	url: 'lms.lms.store.update_member_rank',
	makeParams() {
		return {
			member: memberForm.value.email,
			store: memberForm.value.lms_store || null,
			rank: memberForm.value.store_rank || null,
			full_name: memberForm.value.full_name,
		}
	},
	auto: false,
	onSuccess() {
		showMemberDialog.value = false
		resetForm()
		reloadMembers()
	},
	onError(error) {
		console.error('Error updating member:', error)
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
		reloadMembers()
	},
})

const updateRole = createResource({
	url: 'lms.lms.api.save_role',
	auto: false,
	onSuccess() {
		toast.success(__('Role updated successfully'))
	},
	onError(error) {
		console.error('Error updating role:', error)
		toast.error(__('Failed to update role'))
	},
})

const openNewMemberDialog = () => {
	editingMember.value = null
	resetForm()
	showMemberDialog.value = true
}

const editMember = (member: Member) => {
	editingMember.value = member
	memberForm.value = {
		email: member.name,
		full_name: member.full_name,
		lms_store: member.lms_store || '',
		store_rank: member.store_rank || '',
		role: member.role || '',
	}
	showMemberDialog.value = true
}

const confirmDelete = (member: Member) => {
	deletingMember.value = member
	showDeleteDialog.value = true
}

const saveMember = async () => {
	try {
		if (editingMember.value) {
			await updateMember.submit()
			showMemberDialog.value = false
			resetForm()
			reloadMembers()
		} else {
			await createMember.submit()
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
		lms_store: '',
		store_rank: '',
		role: '',
	}
}

const reloadMembers = () => {
	memberList.value = []
	start.value = 0
	members.reload()
}

watch(search, () => {
	memberList.value = []
	start.value = 0
	members.reload()
})

const getRole = (role: string) => {
	const map: Record<string, string> = {
		'LMS Student': 'Student',
		'Course Creator': 'Instructor',
		Moderator: 'Moderator',
		'Batch Evaluator': 'Evaluator',
	}
	return map[role]
}
</script>
