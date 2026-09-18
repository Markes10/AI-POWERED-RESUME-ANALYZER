import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { 
  Upload, 
  FileText, 
  Brain, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  TrendingUp,
  Award,
  Users,
  Clock,
  Download,
  Save
} from "lucide-react";
import { analyzeResume, uploadVoice, suggestImprovements } from "@/services/resume";
import { AnalysisResult, JobMatch } from "@/types/resume";
import { exportToPDF } from "@/lib/pdfExport";
import { useToast } from "@/hooks/use-toast";

export default function ResumeFit() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [jobDescription, setJobDescription] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [apiResult, setApiResult] = useState<any | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [suggestions, setSuggestions] = useState<string[] | null>(null);
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [audioURL, setAudioURL] = useState<string | null>(null);
  const { toast } = useToast();

  const handleSaveReport = () => {
    if (!analysisResult || !apiResult) return;
    // Save to localStorage or backend
    const reportData = {
      analysisResult,
      apiResult,
      jobDescription,
      resumeFileName: resumeFile?.name || null,
      timestamp: new Date().toISOString(),
    };
    const saved = JSON.parse(localStorage.getItem('savedReports') || '[]');
    saved.push(reportData);
    localStorage.setItem('savedReports', JSON.stringify(saved));
    toast({ title: "Report saved", description: "Analysis report has been saved locally" });
  };

  const handleExportPDF = () => {
    if (!analysisResult || !apiResult) return;
    exportToPDF({
      analysisResult,
      apiResult,
      jobDescription,
      resumeFileName: resumeFile?.name || null,
    });
  };

  const handleAnalyze = async () => {
    if (!resumeFile && !jobDescription) return;

    setIsAnalyzing(true);

    try {
      const apiResult = await analyzeResume(resumeFile, undefined, jobDescription || undefined);
      setApiResult(apiResult);

      // Build a lightweight AnalysisResult from API response
      const overallScore = apiResult.match_score ? Math.round(apiResult.match_score * 100) : 0;

      const skillMatches = (apiResult.skills || []).map((s: string) => ({
        skill: s,
        required: false,
        match: true,
        score: 80,
        category: "General"
      }));

      const result: AnalysisResult = {
        overallScore,
        skillMatches,
        strengths: (skillMatches.slice(0, 4).map((m: any) => `Strong in ${m.skill}`)),
        gaps: [],
        recommendations: [],
        experience: { required: "N/A", candidate: "N/A", match: false },
        education: { required: "N/A", candidate: "N/A", match: false }
      };

      setAnalysisResult(result);
      setShowResults(true);
    } catch (error) {
      console.error("Analysis failed:", error);
      alert("Analysis failed. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleTranscribe = async () => {
    if (!audioFile) return;
    setIsTranscribing(true);
    try {
      const resp = await uploadVoice(audioFile, undefined);
      setApiResult(resp);

      const overallScore = resp.match_score ? Math.round(resp.match_score * 100) : 0;
      const skillMatches = (resp.skills || []).map((s: string) => ({
        skill: s,
        required: false,
        match: true,
        score: 80,
        category: 'General'
      }));

      const result: AnalysisResult = {
        overallScore,
        skillMatches,
        strengths: (skillMatches.slice(0, 4).map((m: any) => `Strong in ${m.skill}`)),
        gaps: [],
        recommendations: [],
        experience: { required: 'N/A', candidate: 'N/A', match: false },
        education: { required: 'N/A', candidate: 'N/A', match: false }
      };

      setAnalysisResult(result);
      setShowResults(true);

      // Request improvement suggestions
      try {
        const resumeText = resp.resume_text || resp.resume_text_preview || '';
        const sug = await suggestImprovements(undefined, resumeText, jobDescription || undefined);
        setSuggestions(sug.suggestions || []);
      } catch (e) {
        console.debug('Suggestions fetch failed', e);
      }
    } catch (error) {
      console.error('Transcription failed', error);
      alert('Transcription failed. Please try again.');
    } finally {
      setIsTranscribing(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream as MediaStream);
      mediaRecorderRef.current = mr;
      chunksRef.current = [];
      mr.ondataavailable = (e: any) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };
      mr.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: chunksRef.current[0]?.type || 'audio/webm' });
        const url = URL.createObjectURL(blob);
        setAudioURL(url);
        const ext = blob.type.includes('ogg') ? 'ogg' : (blob.type.includes('wav') ? 'wav' : 'webm');
        const file = new File([blob], `recording.${ext}`, { type: blob.type });
        setAudioFile(file);
        // Stop tracks
        try {
          stream.getTracks().forEach(t => t.stop());
        } catch (e) {}
      };
      mr.start();
      setRecording(true);
    } catch (e) {
      console.error('Recording failed', e);
      alert('Microphone access is required to record.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      try {
        mediaRecorderRef.current.stop();
      } catch (e) {
        console.error('Failed to stop recorder', e);
      }
      setRecording(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return "bg-green-100";
    if (score >= 60) return "bg-yellow-100";
    return "bg-red-100";
  };

  // Initialize with mock data for demonstration
  const mockAnalysis: AnalysisResult = {
    overallScore: 87,
    skillMatches: [
      { skill: "React", required: true, match: true, score: 95, category: "Frontend" },
      { skill: "TypeScript", required: true, match: true, score: 90, category: "Frontend" },
      { skill: "Node.js", required: true, match: true, score: 85, category: "Backend" },
      { skill: "Python", required: false, match: true, score: 80, category: "Backend" },
      { skill: "AWS", required: true, match: false, score: 0, category: "Cloud" },
      { skill: "Docker", required: false, match: true, score: 70, category: "DevOps" },
      { skill: "GraphQL", required: false, match: false, score: 0, category: "API" },
      { skill: "MongoDB", required: true, match: true, score: 75, category: "Database" },
    ],
    strengths: [
      "Strong frontend development skills with React and TypeScript",
      "Solid backend experience with Node.js and Python",
      "Database experience with MongoDB and PostgreSQL",
      "Good understanding of modern development practices"
    ],
    gaps: [
      "No experience with AWS cloud services",
      "Limited knowledge of GraphQL",
      "Missing containerization experience with Docker"
    ],
    recommendations: [
      "Consider AWS certification to close cloud skills gap",
      "Complete GraphQL tutorial or course",
      "Gain hands-on experience with Docker containers",
      "Highlight existing cloud experience from other platforms"
    ],
    experience: {
      required: "3+ years in full-stack development",
      candidate: "4 years in software development",
      match: true
    },
    education: {
      required: "Bachelor's in Computer Science or related field",
      candidate: "B.S. Computer Science, Stanford University",
      match: true
    }
  };

  // Use mock analysis if no real analysis result is available
  const displayAnalysis = analysisResult || mockAnalysis;

  const highlightText = (text: string, skills: string[] = []) => {
    if (!text) return <span />;
    if (!skills || skills.length === 0) return <span>{text}</span>;
    const escaped = skills.map(s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    const regex = new RegExp(`\\b(${escaped.join('|')})\\b`, 'gi');
    const parts: any[] = [];
    let lastIndex = 0;
    let match: RegExpExecArray | null;
    while ((match = regex.exec(text)) !== null) {
      const start = match.index;
      const end = regex.lastIndex;
      if (start > lastIndex) parts.push(text.slice(lastIndex, start));
      parts.push(<mark key={lastIndex} className="bg-yellow-200 rounded px-0.5">{match[0]}</mark>);
      lastIndex = end;
    }
    if (lastIndex < text.length) parts.push(text.slice(lastIndex));
    return <span>{parts}</span>;
  };

  const getRoleRecommendations = (rolePredictions: any[] | undefined) => {
    if (!rolePredictions || rolePredictions.length === 0) return [];
    const top = rolePredictions[0].role || '';
    const map: Record<string, string[]> = {
      'Data Scientist': ['Add ML project details (datasets, metrics).', 'Show model deployment experience.'],
      'Web Developer': ['Add links to live projects or GitHub.', 'Highlight frontend performance improvements.'],
      'DevOps Engineer': ['Detail CI/CD pipelines and IaC experience.', 'List cloud provider certifications.'],
      'Machine Learning Engineer': ['Show model optimization and serving experience.', 'List relevant frameworks and production infra.']
    };
    return map[top] || [`Tailor resume for ${top} role.`, 'Emphasize quantifiable achievements.'];
  };
  
  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="flex items-center justify-center w-12 h-12 bg-blue-500 rounded-lg">
          <Brain className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">AI Résumé-Job Fit Engine</h1>
          <p className="text-muted-foreground">Intelligent matching system with advanced AI analysis</p>
        </div>
      </div>

      {!showResults ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Job Description Input */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Job Description
              </CardTitle>
              <CardDescription>
                Paste the job description you want to match against
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="job-title">Job Title</Label>
                <Input id="job-title" placeholder="e.g., Senior Full-Stack Developer" />
              </div>
              <div>
                <Label htmlFor="job-description">Description</Label>
                <Textarea
                  id="job-description"
                  placeholder="Paste the full job description here..."
                  className="min-h-[200px]"
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Resume Upload */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Resume Upload
              </CardTitle>
              <CardDescription>
                Upload the candidate's resume for analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed border-muted rounded-lg p-8 text-center">
                <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <div className="space-y-2">
                  <p className="text-sm font-medium">Drop resume here or click to upload</p>
                  <p className="text-xs text-muted-foreground">PDF, DOC, DOCX up to 10MB</p>
                </div>
                <Input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  className="mt-4"
                  onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                />
              </div>
              {resumeFile && (
                <div className="flex items-center gap-2 p-3 bg-muted rounded-lg">
                  <FileText className="h-4 w-4" />
                  <span className="text-sm font-medium">{resumeFile.name}</span>
                </div>
              )}
              {/* Audio upload for voice-based resume */}
              <div className="mt-4 border-2 border-dashed border-muted rounded-lg p-6 text-center">
                <Upload className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
                <div>
                  <p className="text-sm font-medium">Or upload audio (wav/mp3) for speech-to-text</p>
                  <p className="text-xs text-muted-foreground">Audio will be transcribed to resume text</p>
                </div>
                <Input
                  type="file"
                  accept="audio/*"
                  className="mt-4"
                  onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
                />
                <div className="mt-3 flex items-center justify-center gap-3">
                  {!recording ? (
                    <Button onClick={startRecording}>Start Recording</Button>
                  ) : (
                    <Button variant="destructive" onClick={stopRecording}>Stop Recording</Button>
                  )}
                  {audioURL && (
                    <audio controls src={audioURL} className="ml-4" />
                  )}
                </div>
                {audioFile && (
                  <div className="flex items-center gap-2 p-3 bg-muted rounded-lg mt-3">
                    <FileText className="h-4 w-4" />
                    <span className="text-sm font-medium">{audioFile.name}</span>
                  </div>
                )}
                <div className="mt-3">
                  <Button onClick={handleTranscribe} disabled={!audioFile || isTranscribing}>
                    {isTranscribing ? 'Transcribing...' : 'Transcribe & Analyze'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Analyze Button */}
          <div className="lg:col-span-2 flex justify-center">
            <Button
              size="lg"
              onClick={handleAnalyze}
              disabled={isAnalyzing || (!resumeFile && !jobDescription)}
              className="px-8"
            >
              {isAnalyzing ? (
                <>
                  <Brain className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing with AI...
                </>
              ) : (
                <>
                  <Brain className="h-4 w-4 mr-2" />
                  Analyze Fit
                </>
              )}
            </Button>
          </div>
        </div>
      ) : (
        <Tabs defaultValue="overview" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="skills">Skills Analysis</TabsTrigger>
            <TabsTrigger value="experience">Experience</TabsTrigger>
            <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Overall Score */}
            {analysisResult && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="h-5 w-5" />
                    Overall Match Score
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-6">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Compatibility Score</span>
                        <span className={`text-2xl font-bold ${getScoreColor(displayAnalysis.overallScore)}`}>
                          {displayAnalysis.overallScore}%
                        </span>
                      </div>
                      <Progress value={displayAnalysis.overallScore} className="h-3" />
                      <p className="text-sm text-muted-foreground mt-2">
                        {displayAnalysis.overallScore >= 80 ? "Excellent match" : 
                         displayAnalysis.overallScore >= 60 ? "Good match" : "Needs improvement"}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Role Predictions */}
            {apiResult && apiResult.role_predictions && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Role Predictions
                  </CardTitle>
                  <CardDescription>Top predicted roles from the resume</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {apiResult.role_predictions.map((r: any, i: number) => (
                      <div key={i} className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{r.role}</p>
                          <p className="text-sm text-muted-foreground">Confidence: {(r.score * 100).toFixed(0)}%</p>
                        </div>
                        {i === 0 && (
                          <div className="text-sm text-muted-foreground">
                            {getRoleRecommendations(apiResult.role_predictions).map((rec, idx) => (
                              <div key={idx}>{rec}</div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Resume Preview */}
            {apiResult && (apiResult.resume_text || apiResult.resume_text_preview) && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Resume Preview
                  </CardTitle>
                  <CardDescription>Preview of extracted resume text with highlighted skills</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="prose max-w-none">
                    {highlightText((apiResult.resume_text || apiResult.resume_text_preview), apiResult.skills || [])}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Quick Stats */}
            {analysisResult && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <div>
                        <p className="text-2xl font-bold">
                          {displayAnalysis.skillMatches.filter(s => s.match && s.required).length}
                        </p>
                        <p className="text-sm text-muted-foreground">Required Skills Met</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-2">
                      <XCircle className="h-5 w-5 text-red-600" />
                      <div>
                        <p className="text-2xl font-bold">
                          {displayAnalysis.skillMatches.filter(s => !s.match && s.required).length}
                        </p>
                        <p className="text-sm text-muted-foreground">Skills Gaps</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-blue-600" />
                      <div>
                        <p className="text-2xl font-bold">
                          {displayAnalysis.skillMatches.filter(s => s.match && !s.required).length}
                        </p>
                        <p className="text-sm text-muted-foreground">Bonus Skills</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          <TabsContent value="skills" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Skills Breakdown</CardTitle>
                <CardDescription>Detailed analysis of skill requirements vs candidate abilities</CardDescription>
              </CardHeader>
              <CardContent>
                {analysisResult && (
                  <div className="space-y-4">
                    {displayAnalysis.skillMatches.map((skill, index) => (
                      <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-3">
                          {skill.match ? (
                            <CheckCircle className="h-5 w-5 text-green-600" />
                          ) : (
                            <XCircle className="h-5 w-5 text-red-600" />
                          )}
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-medium">{skill.skill}</span>
                              {skill.required && <Badge variant="destructive" className="text-xs">Required</Badge>}
                              <Badge variant="secondary" className="text-xs">{skill.category}</Badge>
                            </div>
                            {skill.match && skill.score > 0 && (
                              <p className="text-sm text-muted-foreground">Proficiency: {skill.score}%</p>
                            )}
                          </div>
                        </div>
                        {skill.match && skill.score > 0 && (
                          <div className="w-24">
                            <Progress value={skill.score} className="h-2" />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="experience" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {analysisResult && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="h-5 w-5" />
                      Experience Requirements
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-start gap-3">
                      {displayAnalysis.experience.match ? (
                        <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
                      )}
                      <div>
                        <p className="font-medium">Experience Match</p>
                        <p className="text-sm text-muted-foreground">Required: {displayAnalysis.experience.required}</p>
                        <p className="text-sm text-muted-foreground">Candidate: {displayAnalysis.experience.candidate}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {analysisResult && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="h-5 w-5" />
                      Education Requirements
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-start gap-3">
                      {displayAnalysis.education.match ? (
                        <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
                      )}
                      <div>
                        <p className="font-medium">Education Match</p>
                        <p className="text-sm text-muted-foreground">Required: {displayAnalysis.education.required}</p>
                        <p className="text-sm text-muted-foreground">Candidate: {displayAnalysis.education.candidate}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="recommendations" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {analysisResult && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-green-600">
                      <CheckCircle className="h-5 w-5" />
                      Strengths
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {displayAnalysis.strengths.map((strength, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm">
                          <div className="w-1.5 h-1.5 bg-green-600 rounded-full mt-2 flex-shrink-0" />
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {analysisResult && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-red-600">
                      <AlertCircle className="h-5 w-5" />
                      Areas for Improvement
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {displayAnalysis.gaps.map((gap, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm">
                          <div className="w-1.5 h-1.5 bg-red-600 rounded-full mt-2 flex-shrink-0" />
                          {gap}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {analysisResult && (
                <Card className="md:col-span-2">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="h-5 w-5" />
                      AI Recommendations
                    </CardTitle>
                    <CardDescription>
                      Personalized suggestions to improve candidate-role fit
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {displayAnalysis.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                          <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center flex-shrink-0">
                            <span className="text-xs text-primary-foreground font-medium">{index + 1}</span>
                          </div>
                          <p className="text-sm">{rec}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
              {((suggestions && suggestions.length > 0) || (apiResult && apiResult.suggestions && apiResult.suggestions.length > 0)) && (
                <Card className="md:col-span-2">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="h-5 w-5" />
                      Suggested Improvements
                    </CardTitle>
                    <CardDescription>Automated suggestions to improve the resume</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {(suggestions || apiResult?.suggestions || []).map((s: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                          <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center flex-shrink-0">
                            <span className="text-xs text-primary-foreground font-medium">{idx + 1}</span>
                          </div>
                          <p className="text-sm">{s}</p>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Action Buttons */}
          <div className="flex gap-4 justify-center pt-6">
            <Button onClick={() => setShowResults(false)} variant="outline">
              New Analysis
            </Button>
            <Button onClick={handleSaveReport}>
              <Save className="h-4 w-4 mr-2" />
              Save Report
            </Button>
            <Button variant="outline" onClick={handleExportPDF}>
              <Download className="h-4 w-4 mr-2" />
              Export PDF
            </Button>
          </div>
        </Tabs>
      )}
    </div>
  );
}
