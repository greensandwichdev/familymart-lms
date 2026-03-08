<template>
	<div class="flex min-h-0 flex-col text-base">
		<div class="flex items-center justify-between">
			<div>
				<div class="text-xl font-semibold mb-1 text-ink-gray-9">
					{{ __(label) }}
				</div>
				<div class="text-ink-gray-6 leading-5">
					{{ __(description) }}
				</div>
			</div>
			<div class="flex item-center space-x-2">
				<Button variant="solid" @click="openNewStore">
					<template #prefix>
						<Plus class="size-4 stroke-1.5" />
					</template>
					{{ __('New Store') }}
				</Button>
			</div>
		</div>

		<div class="mt-8 pb-10">
			<FormControl
				v-model="search"
				:placeholder="__('Search')"
				type="text"
				:debounce="300"
				class="w-1/4 mb-4"
			>
				<template #prefix>
					<Search class="size-4 stroke-1.5 text-ink-gray-5" />
				</template>
			</FormControl>
			<div class="overflow-y-scroll h-[60vh]">
				<ul class="divide-y py-5">
					<li
						v-for="store in storeList"
						:key="store.name"
						class="flex items-center justify-between py-2 cursor-pointer hover:bg-surface-gray-2 px-3 rounded-md"
					>
						<div
							@click="openStore(store)"
							class="flex items-center space-x-3 col-span-2"
						>
							<div class="space-y-1">
								<div class="flex">
									<div class="text-ink-gray-9 font-medium">
										{{ store.store_name }}
									</div>
								</div>
								<div class="text-sm text-ink-gray-7">
									{{ store.store_code }}
								</div>
								<div v-if="store.organization" class="text-sm text-ink-gray-7">
									{{ store.organization }}
								</div>
							</div>
						</div>
						<div class="flex items-center space-x-2">
							<Button variant="ghost" @click.stop="editStore(store)">
								<template #prefix>
									<Pencil class="size-4 stroke-1.5" />
								</template>
							</Button>
							<Button variant="ghost" @click.stop="manageMembers(store)">
								<template #prefix>
									<Users class="size-4 stroke-1.5" />
								</template>
							</Button>
						</div>
					</li>
				</ul>
				<div v-if="!storeList.length" class="text-center py-10 text-ink-gray-6">
					{{ __('No stores found. Create a new store to get started.') }}
				</div>
			</div>
		</div>

		<Dialog v-model="showStoreForm" :options="{ size: 'lg' }">
			<template #body>
				<div class="p-6">
					<div class="text-lg font-semibold mb-4">
						{{ editingStore ? __('Edit Store') : __('New Store') }}
					</div>
					<form @submit.prevent="saveStore">
						<div class="space-y-4">
							<FormControl
								v-model="storeForm.store_name"
								:label="__('Store Name')"
								type="text"
								:required="true"
							/>
							<FormControl
								v-model="storeForm.store_code"
								:label="__('Store Code')"
								type="text"
								:required="true"
							/>
							<FormControl
								v-model="storeForm.organization"
								:label="__('Organization')"
								type="text"
							/>
							<FormControl
								v-model="storeForm.address"
								:label="__('Address')"
								type="textarea"
								:rows="3"
							/>
							<FormControl
								v-model="storeForm.is_active"
								:label="__('Active')"
								type="checkbox"
							/>
						</div>
						<div class="flex justify-end gap-2 mt-6">
							<Button variant="subtle" @click="showStoreForm = false">
								{{ __('Cancel') }}
							</Button>
							<Button variant="solid" type="submit">
								{{ __('Save') }}
							</Button>
						</div>
					</form>
				</div>
			</template>
		</Dialog>

		<Dialog v-model="showMembersDialog" :options="{ size: 'xl' }">
			<template #body>
				<div class="p-6">
					<div class="text-lg font-semibold mb-4">
						{{ __('Members - ') }} {{ selectedStore?.store_name }}
					</div>
					<div class="flex justify-between mb-4">
						<Button variant="solid" @click="showAddMemberForm = true">
							<template #prefix>
								<Plus class="size-4 stroke-1.5" />
							</template>
							{{ __('Add Member') }}
						</Button>
					</div>
					<div class="overflow-y-scroll h-[50vh]">
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
												<Trash2 class="size-4 stroke-1.5" />
											</template>
										</Button>
									</td>
								</tr>
							</tbody>
						</table>
						<div v-if="!storeMembers.length" class="text-center py-10 text-ink-gray-6">
							{{ __('No members in this store.') }}
						</div>
					</div>
				</div>
			</template>
		</Dialog>

		<Dialog v-model="showAddMemberForm" :options="{ size: 'md' }">
			<template #body>
				<div class="p-6">
					<div class="text-lg font-semibold mb-4">
						{{ editingMember ? __('Edit Member Rank') : __('Add Member') }}
					</div>
					<form @submit.prevent="saveMember">
						<div class="space-y-4">
							<FormControl
								v-if="!editingMember"
								v-model="memberForm.user"
								:label="__('User')"
								type="text"
								:placeholder="__('Search user by email or name')"
								:required="true"
							/>
							<FormControl
								v-model="memberForm.rank"
								:label="__('Store Rank')"
								type="select"
								:options="rankOptions"
								:required="true"
							/>
						</div>
						<div class="flex justify-end gap-2 mt-6">
							<Button variant="subtle" @click="showAddMemberForm = false">
								{{ __('Cancel') }}
							</Button>
							<Button variant="solid" type="submit">
								{{ __('Save') }}
							</Button>
						</div>
					</form>
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
	Avatar,
	createResource,
} from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { Plus, Search, Pencil, Users, Trash2 } from 'lucide-vue-next'

const props = defineProps({
	label: String,
	description: String,
})

const search = ref('')
const showStoreForm = ref(false)
const showMembersDialog = ref(false)
const showAddMemberForm = ref(false)
const editingStore = ref(null)
const editingMember = ref(null)
const selectedStore = ref(null)

const storeForm = ref({
	store_name: '',
	store_code: '',
	organization: '',
	address: '',
	is_active: 1,
})

const memberForm = ref({
	user: '',
	rank: '',
})

const stores = createResource({
	url: 'lms.lms.store.get_stores',
	auto: true,
})

const ranks = createResource({
	url: 'lms.lms.store.get_store_ranks',
	auto: true,
})

const createStore = createResource({
	url: 'lms.lms.store.create_store',
	makeParams(values) {
		return {
			data: values,
		}
	},
})

const updateStore = createResource({
	url: 'lms.lms.store.update_store',
	makeParams(values) {
		return {
			store: values.store,
			data: values.data,
		}
	},
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
	return stores.data
})

const rankOptions = computed(() => {
	if (!ranks.data) return []
	return ranks.data.map(r => ({ label: r.rank_name, value: r.name }))
})

const openStore = (store) => {
	editStore(store)
}

const editStore = (store) => {
	editingStore.value = store.name
	storeForm.value = {
		store_name: store.store_name,
		store_code: store.store_code,
		organization: store.organization || '',
		address: store.address || '',
		is_active: store.is_active,
	}
	showStoreForm.value = true
}

const openNewStore = () => {
	editingStore.value = null
	storeForm.value = {
		store_name: '',
		store_code: '',
		organization: '',
		address: '',
		is_active: 1,
	}
	showStoreForm.value = true
}

const saveStore = async () => {
	try {
		if (editingStore.value) {
			await updateStore.submit({
				store: editingStore.value,
				data: storeForm.value,
			})
		} else {
			await createStore.submit(storeForm.value)
		}
		showStoreForm.value = false
		stores.reload()
	} catch (error) {
		console.error('Error saving store:', error)
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
