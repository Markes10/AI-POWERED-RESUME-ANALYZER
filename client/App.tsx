import React from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ResumeFit from "./pages/ResumeFit";
import TurnoverRetention from "./pages/TurnoverRetention";
import InterviewCopilot from "./pages/InterviewCopilot";
import OnboardingJourney from "./pages/OnboardingJourney";
import PerformanceFeedback from "./pages/PerformanceFeedback";
import CompensationAnalyzer from "./pages/CompensationAnalyzer";
import LearningPaths from "./pages/LearningPaths";
import AttendanceDetector from "./pages/AttendanceDetector";
import DiversityInclusion from "./pages/DiversityInclusion";
import AdminRoleModel from "./pages/AdminRoleModel";
import ResumeChat from "./pages/ResumeChat";
import ResumeRanking from "./pages/ResumeRanking";
import ResumeLibrary from "./pages/ResumeLibrary";
import { AuthProvider } from "@/context/AuthContext";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Protected routes */}
              <Route element={<ProtectedRoute />}>
                <Route path="/" element={<Layout><Index /></Layout>} />
                <Route path="/resume-fit" element={<Layout><ResumeFit /></Layout>} />
                <Route path="/turnover-retention" element={<Layout><TurnoverRetention /></Layout>} />
                <Route path="/interview-copilot" element={<Layout><InterviewCopilot /></Layout>} />
                <Route path="/onboarding" element={<Layout><OnboardingJourney /></Layout>} />
                <Route path="/performance" element={<Layout><PerformanceFeedback /></Layout>} />
                <Route path="/compensation" element={<Layout><CompensationAnalyzer /></Layout>} />
                <Route path="/learning-paths" element={<Layout><LearningPaths /></Layout>} />
                <Route path="/attendance" element={<Layout><AttendanceDetector /></Layout>} />
                <Route path="/diversity-inclusion" element={<Layout><DiversityInclusion /></Layout>} />
                <Route path="/admin/role-predictor" element={<Layout><AdminRoleModel /></Layout>} />
                <Route path="/resume-chat" element={<Layout><ResumeChat /></Layout>} />
                <Route path="/resume-ranking" element={<Layout><ResumeRanking /></Layout>} />
                <Route path="/resume-library" element={<Layout><ResumeLibrary /></Layout>} />
              </Route>

              {/* Catch-all */}
              <Route path="*" element={<Layout><NotFound /></Layout>} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}