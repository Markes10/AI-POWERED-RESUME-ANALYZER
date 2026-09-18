import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Upload,
  FileText,
  Search,
  Plus,
  Edit2,
  Trash2,
  Download,
  Loader2,
  CheckCircle,
  AlertCircle,
  Globe,
  Languages,
  RefreshCw,
  XCircle,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface SkillEntry {
  skill: string;
  category?: string;
  aliases?: string[];
}

interface SkillDictionaryResponse {
  language: string;
  count: number;
  skills: string[];
}

interface UploadResult {
  status: string;
  skills_loaded: number;
  language: string;
  file: string;
}

export default function SkillDictionary() {
  const [activeTab, setActiveTab] = useState("view");
  const [language, setLanguage] = useState("en");
  const [searchQuery, setSearchQuery] = useState("");
  const [skills, setSkills] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [csvPreview, setCsvPreview] = useState<SkillEntry[]>([]);
  const { toast } = useToast();

  const fetchSkills = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_URL}/resume/skill-dictionary/${language}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data: SkillDictionaryResponse = await response.json();
        setSkills(data.skills || []);
      }
    } catch (err) {
      console.error("Failed to fetch skills:", err);
      toast({ title: "Error", description: "Failed to load skills", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkills();
  }, [language]);

  const handleCsvChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    if (!file.name.endsWith(".csv")) {
      toast({ title: "Invalid file", description: "Please upload a CSV file", variant: "destructive" });
      return;
    }

    setCsvFile(file);
    
    // Preview CSV
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const lines = text.split("\n").filter(l => l.trim());
      const headers = lines[0]?.split(",").map(h => h.trim().toLowerCase()) || [];
      const skillIndex = headers.indexOf("skill");
      const categoryIndex = headers.indexOf("category");
      const aliasesIndex = headers.indexOf("aliases");
      
      const preview = lines.slice(1, 6).map(line => {
        const cols = line.split(",").map(c => c.trim());
        return {
          skill: cols[skillIndex] || "",
          category: categoryIndex >= 0 ? cols[categoryIndex] : "",
          aliases: aliasesIndex >= 0 ? cols[aliasesIndex]?.split(";").map(a => a.trim()).filter(Boolean) : [],
        };
      }).filter(s => s.skill);
      
      setCsvPreview(preview);
    };
    reader.readAsText(file);
  };

  const handleUpload = async () => {
    if (!csvFile) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append("file", csvFile);
    formData.append("language", language);

    const token = localStorage.getItem('authToken');
    try {
      const response = await fetch(`${API_URL}/resume/skill-dictionary`, {
        method: "POST",
        body: formData,
        headers: { 'Authorization': `Bearer ${token}` },
      });
      
      if (response.ok) {
        const result: UploadResult = await response.json();
        toast({ title: "Success", description: `Loaded ${result.skills_loaded} skills for ${result.language}` });
        setCsvFile(null);
        setCsvPreview([]);
        fetchSkills();
      } else {
        const err = await response.json();
        toast({ title: "Upload failed", description: err.detail, variant: "destructive" });
      }
    } catch (err) {
      toast({ title: "Error", description: "Failed to upload dictionary", variant: "destructive" });
    } finally {
      setUploading(false);
    }
  };

  const downloadDictionary = async () => {
    if (skills.length === 0) return;
    
    const csv = "skill\n" + skills.join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `skills_${language}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredSkills = skills.filter(s => 
    s.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Languages className="h-7 w-7 text-primary" />
            Skill Dictionary Manager
          </h1>
          <p className="text-muted-foreground">Manage custom skill dictionaries for resume analysis</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={downloadDictionary} disabled={skills.length === 0 || loading}>
            <Download className="h-4 w-4 mr-2" />
            Download CSV
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="view">View Dictionary</TabsTrigger>
          <TabsTrigger value="upload">Upload CSV</TabsTrigger>
          <TabsTrigger value="languages">Languages</TabsTrigger>
        </TabsList>

        <TabsContent value="view" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Globe className="h-5 w-5" />
                    Skill Dictionary - {language.toUpperCase()}
                  </CardTitle>
                  <CardDescription>{skills.length} skills loaded</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Select value={language} onValueChange={setLanguage}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Spanish</SelectItem>
                      <SelectItem value="fr">French</SelectItem>
                      <SelectItem value="de">German</SelectItem>
                      <SelectItem value="pt">Portuguese</SelectItem>
                      <SelectItem value="pt_br">Portuguese (Brazil)</SelectItem>
                      <SelectItem value="pt_pt">Portuguese (Portugal)</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button onClick={fetchSkills} disabled={loading}>
                    <RefreshCw className={loading ? "h-4 w-4 animate-spin" : "h-4 w-4"} />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row gap-4 mb-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search skills..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              {loading ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              ) : filteredSkills.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No skills found</h3>
                  <p className="text-muted-foreground">Upload a skill dictionary to get started</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredSkills.map((skill) => (
                    <div key={skill} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                      <span className="font-medium">{skill}</span>
                      <Badge variant="outline" className="text-xs">{language.toUpperCase()}</Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="upload" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Upload Custom Skill Dictionary
              </CardTitle>
              <CardDescription>
                Upload a CSV file to customize the skill dictionary for a specific language.
                Expected columns: skill (required), category (optional), aliases (optional, semicolon-separated)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label htmlFor="language-select">Language</Label>
                <Select value={language} onValueChange={setLanguage}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select language" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="es">Spanish</SelectItem>
                    <SelectItem value="fr">French</SelectItem>
                    <SelectItem value="de">German</SelectItem>
                    <SelectItem value="pt">Portuguese</SelectItem>
                    <SelectItem value="pt_br">Portuguese (Brazil)</SelectItem>
                    <SelectItem value="pt_pt">Portuguese (Portugal)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="border-2 border-dashed border-muted rounded-lg p-8 text-center">
                <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <div className="space-y-2">
                  <p className="text-sm font-medium">Drop CSV file here or click to upload</p>
                  <p className="text-xs text-muted-foreground">Columns: skill (required), category, aliases (semicolon-separated)</p>
                </div>
                <Input
                  type="file"
                  accept=".csv"
                  className="mt-4"
                  onChange={handleCsvChange}
                  disabled={uploading}
                />
              </div>

              {csvFile && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <FileText className="h-5 w-5 text-green-600" />
                      <div>
                        <p className="font-medium">{csvFile.name}</p>
                        <p className="text-sm text-muted-foreground">{(csvFile.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => { setCsvFile(null); setCsvPreview([]); }}
                    >
                      <XCircle className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>

                  {csvPreview.length > 0 && (
                    <div>
                      <Label>Preview (first 5 rows)</Label>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b">
                              <th className="text-left p-2">Skill</th>
                              <th className="text-left p-2">Category</th>
                              <th className="text-left p-2">Aliases</th>
                            </tr>
                          </thead>
                          <tbody>
                            {csvPreview.map((row, idx) => (
                              <tr key={idx} className="border-b">
                                <td className="p-2 font-medium">{row.skill}</td>
                                <td className="p-2 text-muted-foreground">{row.category || "-"}</td>
                                <td className="p-2 text-muted-foreground">{row.aliases.join(", ") || "-"}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>CSV Format Example</CardTitle>
              <CardDescription>Download a template to see the expected format</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-muted p-4 rounded-lg font-mono text-sm overflow-x-auto">
                <pre>{`skill,category,aliases
Python,Programming,python3;py
React,Frontend,reactjs;react.js
AWS,Cloud,amazon web services;amazon-web-services
Docker,DevOps,containerization
Project Management,Soft Skills,pm;project mgmt`}</pre>
              </div>
              <Button
                onClick={() => {
                  const csv = `skill,category,aliases
Python,Programming,python3;py
React,Frontend,reactjs;react.js
AWS,Cloud,amazon web services;amazon-web-services
Docker,DevOps,containerization
Project Management,Soft Skills,pm;project mgmt`;
                  const blob = new Blob([csv], { type: "text/csv" });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = "skill_dictionary_template.csv";
                  a.click();
                  URL.revokeObjectURL(url);
                }}
                variant="outline"
                className="mt-4"
              >
                <Download className="h-4 w-4 mr-2" />
                Download Template
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="languages" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Supported Languages
              </CardTitle>
              <CardDescription>
                Manage skill dictionaries for different languages. Each language has its own skill dictionary.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[
                  { code: "en", name: "English", native: "English", flag: "🇺🇸" },
                  { code: "es", name: "Spanish", native: "Español", flag: "🇪🇸" },
                  { code: "fr", name: "French", native: "Français", flag: "🇫🇷" },
                  { code: "de", name: "German", native: "Deutsch", flag: "🇩🇪" },
                  { code: "pt", name: "Portuguese", native: "Português", flag: "🇵🇹" },
                  { code: "pt_br", name: "Portuguese (Brazil)", native: "Português (Brasil)", flag: "🇧🇷" },
                  { code: "pt_pt", name: "Portuguese (Portugal)", native: "Português (Portugal)", flag: "🇵🇹" },
                ].map((lang) => (
                  <Card key={lang.code} className="transition-all hover:shadow-md">
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-3xl">{lang.flag}</span>
                          <div>
                            <p className="font-medium">{lang.name}</p>
                            <p className="text-sm text-muted-foreground">{lang.native}</p>
                          </div>
                        </div>
                        <Badge variant={language === lang.code ? "default" : "outline"}>
                          {language === lang.code ? "Active" : lang.code}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}