import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Upload,
  FileText,
  Search,
  Trash2,
  Eye,
  Download,
  Loader2,
  Brain,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Resume {
  id: number;
  user_id: number;
  skills: string[];
  created_at: string;
  resume_text?: string;
}

export default function ResumeLibrary() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  const [uploading, setUploading] = useState(false);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  const fetchResumes = async () => {
    const token = localStorage.getItem('authToken');
    if (!token) return;

    try {
      const response = await fetch(`${API_URL}/resume/my-resumes`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setResumes(data);
      }
    } catch (err) {
      console.error("Failed to fetch resumes:", err);
      toast({ title: "Error", description: "Failed to load resumes", variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('authToken');
    try {
      const response = await fetch(`${API_URL}/resume/upload`, {
        method: 'POST',
        body: formData,
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      });

      if (response.ok) {
        toast({ title: "Success", description: "Resume uploaded successfully" });
        fetchResumes();
      } else {
        const error = await response.json();
        toast({ title: "Error", description: error.detail || "Upload failed", variant: "destructive" });
      }
    } catch (err) {
      toast({ title: "Error", description: "Upload failed", variant: "destructive" });
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this resume?")) return;

    const token = localStorage.getItem('authToken');
    try {
      const response = await fetch(`${API_URL}/resume/${id}`, {
        method: 'DELETE',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      });

      if (response.ok) {
        toast({ title: "Deleted", description: "Resume removed successfully" });
        fetchResumes();
      } else {
        toast({ title: "Error", description: "Failed to delete", variant: "destructive" });
      }
    } catch (err) {
      toast({ title: "Error", description: "Failed to delete", variant: "destructive" });
    }
  };

  const handlePreview = (resume: Resume) => {
    setSelectedResume(resume);
    setShowPreview(true);
  };

  const filteredResumes = resumes.filter((resume) => {
    const matchesSearch = resume.skills.some(s =>
      s.toLowerCase().includes(searchQuery.toLowerCase())
    ) || (resume.resume_text?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);
    
    if (activeTab === "all") return matchesSearch;
    if (activeTab === "recent") {
      const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
      return matchesSearch && new Date(resume.created_at) > weekAgo;
    }
    return matchesSearch;
  });

  const getSkillColor = (skill: string) => {
    const colors = [
      "bg-blue-100 text-blue-800",
      "bg-green-100 text-green-800",
      "bg-purple-100 text-purple-800",
      "bg-orange-100 text-orange-800",
      "bg-pink-100 text-pink-800",
      "bg-cyan-100 text-cyan-800",
    ];
    let hash = 0;
    for (let i = 0; i < skill.length; i++) {
      hash = skill.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Brain className="h-7 w-7 text-primary" />
            Resume Library
          </h1>
          <p className="text-muted-foreground">Manage and analyze your uploaded resumes</p>
        </div>
        <Button onClick={() => document.getElementById('resume-upload')?.click()} disabled={uploading}>
          {uploading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Upload className="h-4 w-4 mr-2" />}
          Upload Resume
        </Button>
      </div>

      <input
        id="resume-upload"
        type="file"
        accept=".pdf,.doc,.docx"
        onChange={handleUpload}
        className="hidden"
      />

      <Card>
        <CardHeader>
          <CardTitle>Search & Filter</CardTitle>
          <CardDescription>Find resumes by skills or content</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by skills, keywords..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full sm:w-auto">
              <TabsList>
                <TabsTrigger value="all">All Resumes</TabsTrigger>
                <TabsTrigger value="recent">Recent (7 days)</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : filteredResumes.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No resumes found</h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery ? "Try adjusting your search" : "Upload your first resume to get started"}
            </p>
            {!searchQuery && (
              <Button onClick={() => document.getElementById('resume-upload')?.click()}>
                <Upload className="h-4 w-4 mr-2" />
                Upload Resume
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredResumes.map((resume) => (
            <Card key={resume.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <FileText className="h-5 w-5 text-primary" />
                      <h3 className="font-medium text-lg">Resume #{resume.id}</h3>
                      <Badge variant="secondary">{new Date(resume.created_at).toLocaleDateString()}</Badge>
                      <Badge variant="outline">{resume.skills.length} skills</Badge>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {resume.skills.slice(0, 8).map((skill) => (
                        <Badge key={skill} className={getSkillColor(skill)}>{skill}</Badge>
                      ))}
                      {resume.skills.length > 8 && (
                        <Badge variant="outline">+{resume.skills.length - 8} more</Badge>
                      )}
                    </div>
                    {resume.resume_text && (
                      <p className="mt-3 text-sm text-muted-foreground line-clamp-2">
                        {resume.resume_text.slice(0, 200)}...
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 sm:ml-4">
                    <Button variant="ghost" size="icon" onClick={() => handlePreview(resume)} title="Preview">
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => navigate(`/resume-fit?resumeId=${resume.id}`)} title="Analyze Fit">
                      <Brain className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(resume.id)} title="Delete" className="text-destructive hover:text-destructive">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {showPreview && selectedResume && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="w-full max-w-3xl max-h-[80vh] overflow-hidden">
            <CardHeader className="flex items-center justify-between">
              <CardTitle>Resume Preview</CardTitle>
              <Button variant="ghost" size="icon" onClick={() => setShowPreview(false)}>
                <AlertCircle className="h-5 w-5" />
              </Button>
            </CardHeader>
            <CardContent className="max-h-[60vh] overflow-auto">
              <div className="space-y-3">
                <div>
                  <Label>Skills</Label>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {selectedResume.skills.map((skill) => (
                      <Badge key={skill} className={getSkillColor(skill)}>{skill}</Badge>
                    ))}
                  </div>
                </div>
                {selectedResume.resume_text && (
                  <div>
                    <Label>Content Preview</Label>
                    <div className="mt-1 p-4 bg-muted rounded-lg whitespace-pre-wrap text-sm max-h-96 overflow-auto">
                      {selectedResume.resume_text}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}