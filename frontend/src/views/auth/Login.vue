 <template>
  <div class="container-fluid min-vh-100 d-flex align-items-center justify-content-center bg-light">
    <div class="card shadow" style="width: 400px;">
      <div class="card-body p-4">
        <h4 class="card-title text-center mb-4">Placement Portal</h4>
        <h6 class="text-center text-muted mb-4">Sign in to your account</h6>

        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <div class="mb-3">
          <label class="form-label">Email</label>
          <input
            v-model="email"
            type="email"
            class="form-control"
            placeholder="Enter your email"
          />
        </div>
        <div class="mb-3">
          <label class="form-label">Password</label>
          <input
            v-model="password"
            type="password"
            class="form-control"
            placeholder="Enter your password"
          />
        </div>
        <button
          class="btn btn-primary w-100"
          :disabled="loading"
          @click="handleLogin"
        >
          <span v-if="loading">Signing in...</span>
          <span v-else>Login</span>
        </button>

        <hr />
        <p class="text-center mb-0">
          Don't have an account?
          <router-link to="/register">Register here</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      if (!this.email || !this.password) {
        this.error = 'Email and password are required'
        return
      }

      this.loading = true
      this.error = ''

      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: this.email,
            password: this.password
          })
        })

        const data = await response.json()
        console.log('Login response:', data)

        if (!response.ok) {
          this.error = data.message || 'Login failed'
          return
        }

        localStorage.setItem('token', data.token)
        localStorage.setItem('role', data.role)
        localStorage.setItem('user', JSON.stringify({
          id: data.user_id,
          email: data.email,
          role: data.role
        }))

        this.$store.commit('auth/SET_AUTH', {
          token: data.token,
          role: data.role,
          user: { id: data.user_id, email: data.email, role: data.role }
        })

        console.log('token saved:', localStorage.getItem('token'))
        console.log('role saved:', localStorage.getItem('role'))

        if (data.role === 'admin') {
          this.$router.push('/admin/dashboard')
        } else if (data.role === 'company') {
          this.$router.push('/company/dashboard')
        } else if (data.role === 'student') {
          this.$router.push('/student/dashboard')
        }

      } catch (err) {
        console.log('Error:', err)
        this.error = 'Cannot connect to server. Make sure Flask is running on port 5000.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>