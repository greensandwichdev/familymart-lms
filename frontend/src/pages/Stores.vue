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
					type="select"
					:options="provinceOptions"
					placeholder="All Provinces"
					class="w-48"
					@change="onProvinceChange"
				/>
				<FormControl
					v-model="filters.regency"
					type="select"
					:options="regencyOptions"
					placeholder="All Regencies"
					class="w-48"
					@change="onRegencyChange"
				/>
				<FormControl
					v-model="filters.district"
					type="select"
					:options="districtOptions"
					placeholder="All Districts"
					class="w-48"
				/>
			</div>

			<div
				v-if="storeList.length"
				class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 gap-6"
			>
				<router-link
					v-for="store in storeList"
					:key="store.name"
					:to="{ name: 'StoreDetail', params: { storeName: store.name } }"
				>
					<StoreCard :store="store" />
				</router-link>
			</div>
			<div v-else-if="stores.loading" class="py-10 text-center text-ink-gray-6">
				{{ __('Loading...') }}
			</div>
			<div v-else class="py-10 text-center text-ink-gray-6">
				{{ __('No stores found.') }}
			</div>
		</div>
	</div>
</template>
<script setup>
import {
	Button,
	FormControl,
	Breadcrumbs,
	createResource,
} from 'frappe-ui'
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from 'lucide-vue-next'
import StoreCard from '@/components/StoreCard.vue'
import { sessionStore } from '@/stores/session'
import { usersStore } from '@/stores/user'

const router = useRouter()
const { user } = sessionStore()
const { userResource } = usersStore()

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
		label: __('Stores'),
		route: '/stores',
	},
])

const search = ref('')

const filters = ref({
	province: '',
	regency: '',
	district: '',
})

const stores = createResource({
	url: 'lms.lms.store.get_stores_with_member_count',
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

const storesWithMembers = createResource({
	url: 'lms.lms.store.get_stores_with_member_count',
	auto: true,
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
	districtOptions.value = []
	
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
</script>
