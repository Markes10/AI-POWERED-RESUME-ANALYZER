import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, FileText, Loader2, XCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function BatchUpload() {
  const [files, setFiles] = useState<File[]>([]);
  const [jobDescription, setJobDescription] = useState("");
  const [uploading, setUploading] = useState(false);
  const [tasks, setTasks] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState("upload");
  const { toast } = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFiles = Array.from(e.target.files || []);
    const validFiles = newFiles.filter(f => [".pdf", ".doc", ".docx"].includes("." + f.name.split(".").pop()?.toLowerCase()));
    setFiles(prev => [...prev, ...validFiles]);
    e.target.value = "";
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    setUploading(true);
    const formData = new FormData();
    files.forEach(f => formData.append("files", f));
    if (jobDescription) formData.append("job_description", jobDescription);

    const token = localStorage.getItem('authToken');
    try {
      const response = await fetch(`${API_URL}/resume/batch-upload`, {
        method: "POST",
        body: formData,
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        toast({ title: "Upload started", description: "Batch processing started" });
        setFiles([]);
        setJobDescription("");
      } else {
        const err = await response.json();
        toast({ title: "Upload failed", description: err.detail, variant: "destructive" });
      }
    } catch (err) {
      toast({ title: "Error", description: "Failed to start batch upload", variant: "destructive" });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Upload className="h-7 w-7 text-primary" />
            Batch Resume Upload
          </h1>
          <p className="text-muted-foreground">Upload multiple resumes for batch processing</p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="upload">Upload</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="upload">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Upload Resumes
              </CardTitle>
              <CardDescription>Select multiple PDF/DOC/DOCX files for batch processing</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed border-muted rounded-lg p-8 text-center">
                <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <div className="space-y-2">
                  <p className="text-sm font-medium">Drop resumes here or click to upload</p>
                  <p className="text-xs text-muted-foreground">PDF, DOC, DOCX up to 10MB each</p>
                </div>
                <Input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  multiple
                  className="mt-4"
                  onChange={(e) => {
                    const newFiles = Array.from(e.target.files || []);
                    const validFiles = newFiles.filter(f => [".pdf", ".doc", ".docx"].includes("." + f.name.split(".").pop()?.toLowerCase()));
                    setFiles(prev => [...prev, ...validFiles]);
                    e.target.value = "";
                  }}
                  disabled={uploading}
                />
              </div>

              {files.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium">{files.length} file(s) selected</p>
                  <div className="max-h-60 overflow-y-auto space-y-1">
                    {files.map((file, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-muted rounded">
                        <span className="text-sm truncate max-w-[300px]">{file.name}</span>
                        <span className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</span>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setFiles(prev => prev.filter((_, i) => i !== index))}
                          disabled={uploading}
                        >
                          <XCircle className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <Label htmlFor="job-description">Job Description (Optional)</Label>
                <Textarea
                  id="job-description"
                  placeholder="Paste job description to compute match scores..."
                  className="min-h-[100px]"
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  disabled={uploading}
                />
              </div>

              <Button
                onClick={() => toast({ title: "Upload started", description: "Batch processing started" })}
                disabled={uploading || files.length === 0}
                className="w-full"
              >
                {uploading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Start Batch Upload
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Processing History</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Upload resumes to see processing history here</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}