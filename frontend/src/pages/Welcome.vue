<template>
	<div class="sm:h-screen w-full flex flex-col items-center justify-center p-4">
		<!-- Desktop -->
		<img :src="GreetingDesktopImg" class="hidden sm:block w-11/12 rounded-[60px] shadow-xl" />

		<!-- Mobile -->
		<img :src="GreetingMobileImg" class="block sm:hidden w-full rounded-2xl" />
	</div>
</template>

<script setup>
import GreetingDesktopImg from '@/assets/greeting_desktop.png'
import GreetingMobileImg from '@/assets/greeting_mobile.png'
</script>
