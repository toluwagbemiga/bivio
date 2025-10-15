<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="flex justify-center">
        <img src="/logo.svg" alt="Bivio" class="h-12 w-12" />
      </div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
        Welcome to Bivio POS
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Your financial management solution
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <router-view />
      </div>
    </div>
  </div>
</template>
