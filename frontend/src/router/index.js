import { createRouter, createWebHistory } from 'vue-router'
import StudentProfile from '@/views/student/Profile.vue'
import StudentApplications from '@/views/student/Applications.vue'

import CompanyProfile from '@/views/company/Profile.vue'

import store from '@/store'

import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'
import AdminDashboard from '@/views/admin/Dashboard.vue'
import CompanyDashboard from '@/views/company/Dashboard.vue'
import StudentDashboard from '@/views/student/Dashboard.vue'



import Landing from '@/views/Landing.vue'
import AdminCharts from '@/views/admin/Charts.vue'
import AtsChecker from '@/views/AtsChecker.vue'


const routes = [
  {
    path: '/',
    redirect: '/landing'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guestOnly: true }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/company/dashboard',
    name: 'CompanyDashboard',
    component: CompanyDashboard,
    meta: { requiresAuth: true, role: 'company' }
  },
  {
    path: '/student/dashboard',
    name: 'StudentDashboard',
    component: StudentDashboard,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  },
  {
  path: '/company/profile',
  name: 'CompanyProfile',
  component: CompanyProfile,
  meta: { requiresAuth: true, role: 'company' }
},
  {
  path: '/student/profile',
  name: 'StudentProfile',
  component: StudentProfile,
  meta: { requiresAuth: true, role: 'student' }
},
{
  path: '/student/applications',
  name: 'StudentApplications',
  component: StudentApplications,
  meta: { requiresAuth: true, role: 'student' }
},


{
  path: '/landing',
  name: 'Landing',
  component: Landing,
  meta: { guestOnly: false, public: true }  
},
{
  path: '/admin/charts',
  name: 'AdminCharts',
  component: AdminCharts,
  meta: { requiresAuth: true, role: 'admin' }
},
{
  path: '/ats',
  name: 'AtsChecker',
  component: AtsChecker,
  meta: { requiresAuth: true }
}




]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(function(to, from, next) {
  const token = store.getters['auth/isLoggedIn'] || !!localStorage.getItem('token')
  const userRole = store.getters['auth/userRole'] || localStorage.getItem('role')

  if (to.meta.guestOnly && token) {
    if (userRole === 'admin') return next('/admin/dashboard')
    if (userRole === 'company') return next('/company/dashboard')
    if (userRole === 'student') return next('/student/dashboard')
  }

  if (to.meta.requiresAuth) {
    if (!token) return next('/login')
    if (to.meta.role && to.meta.role !== userRole) {
      if (userRole === 'admin') return next('/admin/dashboard')
      if (userRole === 'company') return next('/company/dashboard')
      if (userRole === 'student') return next('/student/dashboard')
    }
  }

  next()
})

export default router