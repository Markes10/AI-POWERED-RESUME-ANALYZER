import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Download,
  FileText,
  Building,
  Briefcase,
  User,
  Calendar,
  Search,
  Loader2,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  Eye,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Resume {
  id: number;
  user_id: number;
  tenant_id: number;
  skills: string[];
  resume_text?: string;
  created_at: string;
}

interface ExportData {
  format: "json" | "workday" | "bamboohr";
  resume: Resume;
}

export default function ResumeExport() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedResume, setSelectedResume] = useState<Resume | null>(null);
  const [exportFormat, setExportFormat] = useState<"json" | "workday" | "bamboohr">("json");
  const [exporting, setExporting] = useState(false);
  const { toast } = useToast();

  const fetchResumes = async () => {
    const token = localStorage.getItem("authToken");
    try {
      const response = await fetch(`${API_URL}/resume/my-resumes`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setResumes(data);
      }
    } catch (err) {
      console.error("Failed to fetch resumes:", err);
      toast({ title: "Error", description: "Failed to load resumes", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const handleExport = async (resume: Resume, format: "json" | "workday" | "bamboohr") => {
    setExporting(true);
    try {
      const token = localStorage.getItem("authToken");
      const response = await fetch(`${API_URL}/resume/${resume.id}/export?format=${format}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `resume-${resume.id}-${format}.json`;
        a.click();
        URL.revokeObjectURL(url);

        toast({ title: "Export successful", description: `Resume exported as ${format.toUpperCase()}` });
      } else {
        const err = await response.json();
        toast({ title: "Export failed", description: err.detail, variant: "destructive" });
      }
    } catch (err) {
      console.error("Export error:", err);
      toast({ title: "Export failed", description: "An error occurred", variant: "destructive" });
    } finally {
      setExporting(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <FileText className="h-7 w-7 text-primary" />
            HRIS Resume Export
          </h1>
          <p className="text-muted-foreground">Export resumes in HRIS-compatible formats</p>
        </div>
      <Card>
        <CardHeader>
          <CardTitle>Export Formats</CardTitle>
          <CardDescription>Choose the target HRIS system for your export</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card
              className={`border-2 ${exportFormat === "json" ? "border-primary" : ""}`}
              onClick={() => setExportFormat("json")}
            >
              <CardContent className="pt-6">
                <div className="text-center">
                  <FileText className="h-12 w-12 text-primary mx-auto mb-3" />
                  <h3 className="font-semibold mb-1">JSON (Generic)</h3>
                  <p className="text-sm text-muted-foreground">Universal format for any system</p>
                </div>
              </CardContent>
            </Card>
            <Card
              className={`border-2 ${exportFormat === "workday" ? "border-primary" : ""}`}
              onClick={() => setExportFormat("workday")}
            >
              <CardContent className="pt-6">
                <div className="text-center">
                  <Building className="h-12 w-12 text-green-600 mx-auto mb-3" />
                  <h3 className="font-semibold mb-1">Workday</h3>
                  <p className="text-sm text-muted-foreground">Workday-compatible format</p>
                </div>
              </CardContent>
            </Card>
            <Card className={`border-2 ${exportFormat === "bamboohr" ? "border-primary" : ""}`} onClick={() => setExportFormat("bamboohr")}>
              <CardContent className="pt-6">
                <div className="text-center">
                  <Briefcase className="h-12 w-12 text-blue-600 mx-auto mb-3" />
                  <h3 className="font-semibold mb-1">BambooHR</h3>
                  <p className="text-sm text-muted-foreground">BambooHR-compatible format</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Your Resumes</h3>
              <p className="text-sm text-muted-foreground">Select a resume to export</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : resumes.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No resumes found</h3>
              <p className="text-muted-foreground">Upload a resume first to export</p>
            </div>
          ) : (
            <div className="space-y-4">
              {resumes.map((resume) => (
                <Card key={resume.id} className="border-l-4 border-l-blue-500">
                  <CardContent className="pt-6">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          <FileText className="h-5 w-5 text-primary" />
                          <h3 className="font-medium text-lg">Resume #{resume.id}</h3>
                          <Badge variant="secondary">{new Date(resume.created_at).toLocaleDateString()}</Badge>
                          <Badge variant="outline">{resume.skills.length} skills</Badge>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {resume.skills.slice(0, 8).map((skill) => (
                            <Badge key={skill} variant="secondary" className="text-xs">{skill}</Badge>
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
                      <div className="flex items-center gap-2 md:ml-4">
                        <Select value={exportFormat} onValueChange={(value) => setExportFormat(value as "json" | "workday" | "bamboohr")}>
                          <SelectTrigger className="w-[160px]">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="json">JSON</SelectItem>
                            <SelectItem value="workday">Workday</SelectItem>
                            <SelectItem value="bamboohr">BambooHR</SelectItem>
                          </SelectContent>
                        </Select>
                        <Button
                          onClick={() => handleExport(resume, exportFormat)}
                          disabled={exporting}
                          className="whitespace-nowrap"
                        >
                          {exporting ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              Exporting...
                            </>
                          ) : (
                            <>
                              <Download className="h-4 w-4 mr-2" />
                              Export {exportFormat.toUpperCase()}
                            </>
                          )}
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => {}}>
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Briefcase className="h-5 w-5" />
            Format Specifications
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="json" className="space-y-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="json">JSON (Generic)</TabsTrigger>
              <TabsTrigger value="workday">Workday</TabsTrigger>
              <TabsTrigger value="bamboohr">BambooHR</TabsTrigger>
            </TabsList>

            <TabsContent value="json" className="space-y-4">
              <h4 className="font-semibold">JSON Generic Format</h4>
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
                <code>{`{
  "resume_id": 123,
  "user_id": 456,
  "skills": ["Python", "React", "AWS"],
  "created_at": "2024-01-15T10:30:00Z",
  "text_preview": "Experienced developer..."
`}</code></pre>
              </TabsContent>

            <TabsContent value="workday" className="space-y-4">
              <h4 className="font-semibold">Workday Format</h4>
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm"><code>{`{
  "Worker_Data": {
    "Worker_ID": "456",
    "Resume": {
      "Resume_ID": "123",
      "Skills": [
        {"Skill_Name": "Python"},
        {"Skill_Name": "React"},
        {"Skill_Name": "AWS"}
      ],
      "Resume_Text": "Experienced developer...",
      "Created_Date": "2024-01-15T10:30:00Z"
    }
  }
`}</code></pre>
              </TabsContent>

            <TabsContent value="bamboohr" className="space-y-4">
              <h4 className="font-semibold">BambooHR Format</h4>
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm"><code>{`{
  "employeeId": 456,
  "resume": {
    "id": 123,
    "skills": ["Python", "React", "AWS"],
    "text": "Experienced developer...",
    "dateCreated": "2024-01-15T10:30:00Z"
  }
`}</code></pre>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}