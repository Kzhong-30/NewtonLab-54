<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content page-container">
        <div class="logo" @click="goHome">
          <el-icon :size="28" color="#409eff"><Gamepad /></el-icon>
          <span class="logo-text">剧本杀</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          router
          class="nav-menu"
          background-color="transparent"
          text-color="#303133"
          active-text-color="#409eff"
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/scripts">剧本库</el-menu-item>
          <el-menu-item index="/games">组局</el-menu-item>
          <el-menu-item index="/community">社区</el-menu-item>
        </el-menu>
        <div class="user-section">
          <template v-if="userStore.isLoggedIn">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
                <span class="username">{{ userStore.user?.username || "用户" }}</span>
                <el-icon><CaretBottom /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon> 个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>
                    <el-icon><SwitchButton /></el-icon> 退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button type="primary" @click="showLoginDialog = true">登录</el-button>
            <el-button @click="showRegisterDialog = true">注册</el-button>
          </template>
        </div>
      </div>
    </el-header>

    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

    <el-footer class="app-footer">
      <div class="footer-content page-container">
        <p>&copy; 2024 剧本杀 - 沉浸式推理体验</p>
      </div>
    </el-footer>
  </el-container>

  <el-dialog
    v-model="showLoginDialog"
    title="登录"
    width="400px"
    :close-on-click-modal="false"
  >
    <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-width="80px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="loginForm.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showLoginDialog = false">取消</el-button>
      <el-button type="primary" @click="handleLogin" :loading="loginLoading">登录</el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="showRegisterDialog"
    title="注册"
    width="400px"
    :close-on-click-modal="false"
  >
    <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-width="80px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="registerForm.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="registerForm.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showRegisterDialog = false">取消</el-button>
      <el-button type="primary" @click="handleRegister" :loading="registerLoading">注册</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const showLoginDialog = ref(false)
const showRegisterDialog = ref(false)
const loginLoading = ref(false)
const registerLoading = ref(false)

const loginFormRef = ref(null)
const registerFormRef = ref(null)

const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({ username: '', email: '', password: '', confirmPassword: '' })

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, type: 'email', message: '请输入正确的邮箱', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: '密码至少6位', trigger: 'blur' }],
  confirmPassword: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }]
}

const goHome = () => router.push('/')

const handleLogin = async () => {
  try {
    await loginFormRef.value.validate()
    loginLoading.value = true
    await userStore.login(loginForm)
    showLoginDialog.value = false
    ElMessage.success('登录成功')
    loginForm.username = ''
    loginForm.password = ''
  } catch (error) {
    if (error.message) ElMessage.error(error.message)
    else ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loginLoading.value = false
  }
}

const handleRegister = async () => {
  try {
    await registerFormRef.value.validate()
    registerLoading.value = true
    await userStore.register(registerForm)
    showRegisterDialog.value = false
    ElMessage.success('注册成功，请登录')
    showLoginDialog.value = true
    Object.assign(registerForm, { username: '', email: '', password: '', confirmPassword: '' })
  } catch (error) {
    if (error.message) ElMessage.error(error.message)
    else ElMessage.error('注册失败')
  } finally {
    registerLoading.value = false
  }
}

const handleCommand = async (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
      userStore.logout()
      ElMessage.success('已退出登录')
      if (route.meta.requiresAuth) router.push('/')
    } catch {}
  }
}

onMounted(() => {
  if (userStore.token) userStore.fetchUser().catch(() => {})
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  flex-direction: column;
}

.app-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.nav-menu {
  border-bottom: none;
  flex: 1;
  margin: 0 24px;
  justify-content: center;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-size: 14px;
  color: #606266;
}

.app-main {
  flex: 1;
  padding: 24px 0;
}

.app-footer {
  background: #fff;
  border-top: 1px solid #e4e7ed;
  text-align: center;
  color: #909399;
  font-size: 12px;
  padding: 16px 0;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
