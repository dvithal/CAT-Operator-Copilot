import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useState } from 'react'
import Sidebar from './components/Sidebar.jsx'
import TopBar from './components/TopBar.jsx'
import CommandCenter from './pages/CommandCenter.jsx'
import MachinePage from './pages/MachinePage.jsx'
import SafetyPage from './pages/SafetyPage.jsx'
import TasksPage from './pages/TasksPage.jsx'
import WeatherPage from './pages/WeatherPage.jsx'
import CopilotPage from './pages/CopilotPage.jsx'
import TrainingPage from './pages/TrainingPage.jsx'
import ReportsPage from './pages/ReportsPage.jsx'
import FleetPage from './pages/FleetPage.jsx'
import SupportPage from './pages/SupportPage.jsx'

export default function App() {
  const [machineId, setMachineId] = useState('EXC001')

  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <TopBar
            machineId={machineId}
            onMachineChange={setMachineId}
          />
          <main className="flex-1 overflow-y-auto bg-surface-900 p-6">
            <Routes>
              <Route path="/"         element={<CommandCenter machineId={machineId} />} />
              <Route path="/machine"  element={<MachinePage   machineId={machineId} />} />
              <Route path="/safety"   element={<SafetyPage    machineId={machineId} />} />
              <Route path="/tasks"    element={<TasksPage     machineId={machineId} />} />
              <Route path="/weather"  element={<WeatherPage   machineId={machineId} />} />
              <Route path="/copilot"  element={<CopilotPage   machineId={machineId} />} />
              <Route path="/training" element={<TrainingPage  machineId={machineId} />} />
              <Route path="/reports"  element={<ReportsPage   machineId={machineId} />} />
              <Route path="/fleet"    element={<FleetPage     machineId={machineId} onSelect={setMachineId} />} />
              <Route path="/support"  element={<SupportPage   machineId={machineId} />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}
