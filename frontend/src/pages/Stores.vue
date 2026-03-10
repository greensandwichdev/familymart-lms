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
					{{ __('Stores') }}
				</div>
				<div class="text-ink-gray-6 mt-1">
					{{ __('Manage stores and their members') }}
				</div>
			</div>

			<div class="mb-4 flex items-center gap-4">
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
				<FormControl
					v-model="filters.province"
					:label="__('Province')"
					type="select"
					:options="provinceOptions"
					placeholder="All Provinces"
					class="w-48"
					@change="onProvinceChange"
				/>
				<FormControl
					v-model="filters.regency"
					:label="__('Regency')"
					type="select"
					:options="regencyOptions"
					placeholder="All Regencies"
					class="w-48"
					:disabled="!filters.province"
					@change="onRegencyChange"
				/>
				<FormControl
					v-model="filters.district"
					:label="__('District')"
					type="select"
					:options="districtOptions"
					placeholder="All Districts"
					class="w-48"
					:disabled="!filters.regency"
				/>
			</div>

			<ListView
				v-if="storeList.length"
				:columns="storeColumns"
				:rows="storeList"
				row-key="name"
				:options="{ showTooltip: false, selectable: false }"
			>
				<ListHeader class="mb-2 grid items-center space-x-4 rounded bg-surface-gray-2 p-2">
					<ListHeaderItem :item="item" v-for="item in storeColumns" />
				</ListHeader>
				<ListRows>
					<ListRow
						v-for="row in storeList"
						:row="row"
						@click="manageMembers(row)"
					>
						<template #default="{ column, item }">
							<ListRowItem :item="row[column.key]" :align="column.align">
								<div v-if="column.key === 'actions'">
									<Button variant="ghost" @click.stop="manageMembers(row)">
										<template #prefix>
											<Users class="size-4 stroke-1.5" />
										</template>
										{{ __('Members') }}
									</Button>
								</div>
								<div v-else-if="column.key === 'store_name'">
									<div class="font-medium text-ink-gray-9">{{ row.store_name }}</div>
								</div>
								<div v-else-if="column.key === 'store_code'">
									<div class="text-sm text-ink-gray-7">{{ row.store_code }}</div>
								</div>
								<div v-else-if="column.key === 'organization'">
									<div class="text-sm text-ink-gray-7">{{ row.organization || '-' }}</div>
								</div>
								<div v-else>
									{{ row[column.key] }}
								</div>
							</ListRowItem>
						</template>
					</ListRow>
				</ListRows>
			</ListView>
			<div v-else-if="stores.loading" class="py-10 text-center text-ink-gray-6">
				{{ __('Loading...') }}
			</div>
			<div v-else class="py-10 text-center text-ink-gray-6">
				{{ __('No stores found.') }}
			</div>
		</div>

		<Dialog v-model="showMembersDialog" :options="{ size: 'xl' }">
			<template #body>
				<div class="p-6">
					<div class="mb-4 text-lg font-semibold">
						{{ __('Members - ') }} {{ selectedStore?.store_name }}
					</div>
					<div class="mb-4 flex justify-between">
						<Button variant="solid" @click="showAddMemberForm = true">
							<template #prefix>
								<Plus class="size-4 stroke-1.5" />
							</template>
							{{ __('Add Member') }}
						</Button>
					</div>
					<div class="max-h-[50vh] overflow-y-auto">
						<table class="w-full">
							<thead class="bg-surface-gray-2">
								<tr>
									<th class="text-left p-3">{{ __('Name') }}</th>
									<th class="text-left p-3">{{ __('Email') }}</th>
									<th class="text-left p-3">{{ __('Rank') }}</th>
									<th class="text-left p-3">{{ __('Actions') }}</th>
								</tr>
							</thead>
							<tbody class="divide-y">
								<tr v-for="member in storeMembers" :key="member.name">
									<td class="p-3">{{ member.full_name }}</td>
									<td class="p-3">{{ member.email }}</td>
									<td class="p-3">{{ member.rank_name || '-' }}</td>
									<td class="p-3">
										<Button variant="ghost" @click="editMemberRank(member)">
											<template #prefix>
												<Pencil class="size-4 stroke-1.5" />
											</template>
										</Button>
										<Button variant="ghost" @click="removeMemberAction(member)">
											<template #prefix>
												<Trash2 class="size-4 stroke-1.5 text-red-500" />
											</template>
										</Button>
									</td>
								</tr>
							</tbody>
						</table>
						<div v-if="!storeMembers.length" class="py-8 text-center text-ink-gray-6">
							{{ __('No members in this store.') }}
						</div>
					</div>
				</div>
			</template>
		</Dialog>

		<Dialog
			v-model="showAddMemberForm"
			:options="{
				title: editingMember ? __('Edit Member Rank') : __('Add Member'),
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
				<div v-if="!editingMember" class="mb-4">
					<FormControl
						v-model="memberForm.user"
						:label="__('Email')"
						placeholder="user@example.com"
						type="email"
						class="w-full"
					/>
				</div>
				<div class="flex items-center">
					<Link
						class="w-full"
						v-model="memberForm.rank"
						doctype="Store Rank"
						:label="__('Store Rank')"
						:filters="{ is_active: 1 }"
						placeholder="Select rank"
					/>
				</div>
			</template>
		</Dialog>
	</div>
</template>
<script setup>
import {
	Button,
	Dialog,
	FormControl,
	Breadcrumbs,
	ListView,
	ListHeader,
	ListHeaderItem,
	ListRows,
	ListRow,
	ListRowItem,
	createResource,
} from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { Plus, Search, Users, Trash2, Pencil } from 'lucide-vue-next'
import Link from '@/components/Controls/Link.vue'

const breadcrumbs = computed(() => [
	{
		label: __('Stores'),
		route: '/stores',
	},
])

const storeColumns = computed(() => [
	{
		label: __('Store Name'),
		key: 'store_name',
		width: 2,
	},
	{
		label: __('Store Code'),
		key: 'store_code',
		width: 1,
	},
	{
		label: __('Organization'),
		key: 'organization',
		width: 2,
	},
	{
		label: __('Actions'),
		key: 'actions',
		width: 1,
		align: 'right',
	},
])

const search = ref('')
const showMembersDialog = ref(false)
const showAddMemberForm = ref(false)
const editingMember = ref(null)
const selectedStore = ref(null)

const filters = ref({
	province: '',
	regency: '',
	district: '',
})

const memberForm = ref({
	user: '',
	rank: '',
})

const stores = createResource({
	url: 'lms.lms.store.get_stores',
	auto: true,
	transform(data) {
		return data.map(store => ({
			...store,
			province: store.province || '',
			regency: store.regency || '',
			district: store.district || '',
		}))
	},
})

const provinces = createResource({
	url: 'lms.lms.store.get_provinces',
	auto: true,
})

const getRegencies = createResource({
	url: 'lms.lms.store.get_regencies',
})

const getDistricts = createResource({
	url: 'lms.lms.store.get_districts',
})

const ranks = createResource({
	url: 'lms.lms.store.get_store_ranks',
	auto: true,
})

const getStoreMembers = createResource({
	url: 'lms.lms.store.get_store_members',
})

const removeMember = createResource({
	url: 'lms.lms.store.remove_member_from_store',
	makeParams(values) {
		return {
			member: values.member,
		}
	},
})

const updateMemberRank = createResource({
	url: 'lms.lms.store.update_member_rank',
	makeParams(values) {
		return {
			member: values.member,
			rank: values.rank,
		}
	},
})

const assignMember = createResource({
	url: 'lms.lms.store.assign_member_to_store',
	makeParams(values) {
		return {
			member: values.member,
			store: values.store,
			rank: values.rank,
		}
	},
})

const storeMembers = ref([])

const storeList = computed(() => {
	if (!stores.data) return []
	let result = stores.data

	if (search.value) {
		const searchLower = search.value.toLowerCase()
		result = result.filter(
			store =>
				store.store_name.toLowerCase().includes(searchLower) ||
				store.store_code.toLowerCase().includes(searchLower) ||
				(store.organization && store.organization.toLowerCase().includes(searchLower))
		)
	}

	if (filters.value.province) {
		result = result.filter(store => store.province === filters.value.province)
	}
	if (filters.value.regency) {
		result = result.filter(store => store.regency === filters.value.regency)
	}
	if (filters.value.district) {
		result = result.filter(store => store.district === filters.value.district)
	}

	return result
})

const provinceOptions = computed(() => {
	if (!provinces.data) return []
	return [{ label: 'All Provinces', value: '' }, ...provinces.data.map(p => ({ label: p.name, value: p.name }))]
})

const regencyOptions = ref([])

const districtOptions = ref([])

const onProvinceChange = async () => {
	filters.value.regency = ''
	filters.value.district = ''
	if (filters.value.province) {
		try {
			const regencies = await getRegencies.submit({ province: filters.value.province })
			regencyOptions.value = [{ label: 'All Regencies', value: '' }, ...regencies.map(r => ({ label: r.name, value: r.name }))]
		} catch (e) {
			console.error('Error fetching regencies:', e)
		}
	}
}

const onRegencyChange = async () => {
	filters.value.district = ''
	if (filters.value.regency) {
		try {
			const districts = await getDistricts.submit({ regency: filters.value.regency })
			districtOptions.value = [{ label: 'All Districts', value: '' }, ...districts.map(d => ({ label: d.name, value: d.name }))]
		} catch (e) {
			console.error('Error fetching districts:', e)
		}
	}
}

const manageMembers = async (store) => {
	selectedStore.value = store
	showMembersDialog.value = true
	loadMembers()
}

const loadMembers = async () => {
	if (!selectedStore.value) return
	try {
		const members = await getStoreMembers.submit({
			store: selectedStore.value.name,
		})
		storeMembers.value = members
	} catch (error) {
		console.error('Error loading members:', error)
	}
}

const editMemberRank = (member) => {
	editingMember.value = member
	memberForm.value = {
		user: member.name,
		rank: member.store_rank,
	}
	showAddMemberForm.value = true
}

const removeMemberAction = async (member) => {
	if (!confirm(`Remove ${member.full_name} from this store?`)) return
	try {
		await removeMember.submit({
			member: member.name,
		})
		loadMembers()
	} catch (error) {
		console.error('Error removing member:', error)
	}
}

const saveMember = async () => {
	try {
		if (editingMember.value) {
			await updateMemberRank.submit({
				member: editingMember.value.name,
				rank: memberForm.value.rank,
			})
		} else {
			await assignMember.submit({
				member: memberForm.value.user,
				store: selectedStore.value.name,
				rank: memberForm.value.rank,
			})
		}
		showAddMemberForm.value = false
		editingMember.value = null
		memberForm.value = { user: '', rank: '' }
		loadMembers()
	} catch (error) {
		console.error('Error saving member:', error)
	}
}

watch(showAddMemberForm, (val) => {
	if (!val) {
		editingMember.value = null
		memberForm.value = { user: '', rank: '' }
	}
})
</script>
