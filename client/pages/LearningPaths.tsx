"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { getLearningPaths, getSkills, getRecommendations, getAchievements } from "@/services/learning";
import { 
  BookOpen, 
  Target, 
  Star, 
  Clock, 
  Award,
  TrendingUp,
  Play,
  CheckCircle,
  Users,
  Lightbulb,
  Brain,
  Filter,
  Search,
  Calendar,
  BarChart3,
  Video,
  FileText,
  Headphones,
  Monitor,
  Coffee,
  Zap
} from "lucide-react";

interface LearningPath {
  id: number;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  duration: string;
  total_modules: number;
  completed_modules: number;
  progress: number;
  skills: string[];
  format: string[];
  rating: number;
  enrollment_count: number;
  created_at: string;
  updated_at: string;
}

interface Skill {
  id: number;
  name: string;
  current_level: number;
  target_level: number;
  priority: string;
  category: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  importance: string;
}

interface Recommendation {
  id: number;
  title: string;
  type: string;
  provider: string;
  duration: string;
  difficulty: string;
  relevance_score: number;
  description: string;
  skills: string[];
  cost: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export default function LearningPaths() {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedDifficulty, setSelectedDifficulty] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

  const {
    data: learningPaths = [],
    isLoading: isLoadingPaths
  } = useQuery({
    queryKey: ['learningPaths'],
    queryFn: getLearningPaths
  });

  const {
    data: skillGaps = [],
    isLoading: isLoadingSkills
  } = useQuery({
    queryKey: ['skills'],
    queryFn: getSkills
  });

  const {
    data: recommendations = [],
    isLoading: isLoadingRecommendations
  } = useQuery({
    queryKey: ['recommendations'],
    queryFn: getRecommendations
  });

  const {
    data: achievements = [],
    isLoading: isLoadingAchievements
  } = useQuery({
    queryKey: ['achievements'],
    queryFn: getAchievements
  });

  if (isLoadingPaths || isLoadingSkills || isLoadingRecommendations || isLoadingAchievements) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "Beginner": return "bg-green-100 text-green-600";
      case "Intermediate": return "bg-yellow-100 text-yellow-600";
      case "Advanced": return "bg-red-100 text-red-600";
      default: return "bg-gray-100 text-gray-600";
    }
  };

  const getImportanceColor = (priority: string) => {
    switch (priority) {
      case "High": return "text-red-600";
      case "Medium": return "text-yellow-600";
      case "Low": return "text-green-600";
      default: return "text-gray-600";
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "Course": return <Video className="h-4 w-4" />;
      case "Certification": return <Award className="h-4 w-4" />;
      case "Workshop": return <Users className="h-4 w-4" />;
      case "Mentoring": return <Coffee className="h-4 w-4" />;
      case "Conference": return <Monitor className="h-4 w-4" />;
      default: return <BookOpen className="h-4 w-4" />;
    }
  };

  const getFormatIcon = (format: string) => {
    switch (format) {
      case "Video": return <Video className="h-3 w-3" />;
      case "Reading": return <FileText className="h-3 w-3" />;
      case "Practice": return <Target className="h-3 w-3" />;
      case "Projects": return <Monitor className="h-3 w-3" />;
      case "Coding": return <Monitor className="h-3 w-3" />;
      case "Audio": return <Headphones className="h-3 w-3" />;
      default: return <BookOpen className="h-3 w-3" />;
    }
  };

  const totalProgress = learningPaths.length ? learningPaths.reduce((sum, path) => sum + path.progress, 0) / learningPaths.length : 0;
  const completedPaths = learningPaths.filter(path => path.progress === 100).length;
  const inProgressPaths = learningPaths.filter(path => path.progress > 0 && path.progress < 100).length;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="flex items-center justify-center w-12 h-12 bg-indigo-500 rounded-lg">
          <BookOpen className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">AI Learning-Path Recommender</h1>
          <p className="text-muted-foreground">Personalized learning recommendations based on career goals and skill gaps</p>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-2xl font-bold">{Math.round(totalProgress)}%</p>
                <p className="text-sm text-muted-foreground">Avg Progress</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-2xl font-bold">{completedPaths}</p>
                <p className="text-sm text-muted-foreground">Completed Paths</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-2xl font-bold">{inProgressPaths}</p>
                <p className="text-sm text-muted-foreground">In Progress</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-2xl font-bold">{skillGaps.filter(s => s.priority === "High").length}</p>
                <p className="text-sm text-muted-foreground">Priority Skills</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="my-paths" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="my-paths">My Learning Paths</TabsTrigger>
          <TabsTrigger value="recommendations">AI Recommendations</TabsTrigger>
          <TabsTrigger value="skill-gaps">Skill Gap Analysis</TabsTrigger>
          <TabsTrigger value="catalog">Course Catalog</TabsTrigger>
          <TabsTrigger value="analytics">Learning Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="my-paths" className="space-y-6">
          <div className="grid gap-6">
            {learningPaths.map((path) => (
              <Card key={path.id} className="border-l-4 border-l-indigo-500">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-semibold text-lg">{path.title}</h3>
                        <Badge className={getDifficultyColor(path.difficulty)}>
                          {path.difficulty}
                        </Badge>
                        <Badge variant="outline">{path.category}</Badge>
                      </div>
                      <p className="text-muted-foreground mb-4">{path.description}</p>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{path.duration}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <BookOpen className="h-4 w-4 text-muted-foreground" />
                                                    <span className="text-sm">{path.completed_modules}/{path.total_modules} modules</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Star className="h-4 w-4 text-yellow-500" />
                                                    <span className="text-sm">{path.rating} ({path.enrollment_count} enrolled)</span>
                        </div>
                      </div>

                      <div className="mb-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">Progress</span>
                          <span className="text-sm text-muted-foreground">{path.progress}% complete</span>
                        </div>
                        <Progress value={path.progress} className="h-2" />
                      </div>

                      <div className="flex flex-wrap gap-1 mb-4">
                        <span className="text-sm text-muted-foreground mr-2">Skills:</span>
                        {path.skills.map((skill, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {skill}
                          </Badge>
                        ))}
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">Format:</span>
                        {path.format.map((format, index) => (
                          <div key={index} className="flex items-center gap-1">
                            {getFormatIcon(format)}
                            <span className="text-xs">{format}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="flex flex-col gap-2 min-w-[120px]">
                      <Button size="sm" className="w-full">
                        <Play className="h-3 w-3 mr-1" />
                        Continue
                      </Button>
                      <Button size="sm" variant="outline" className="w-full">
                        View Details
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                AI-Powered Learning Recommendations
              </CardTitle>
              <CardDescription>
                Personalized suggestions based on your role, goals, and skill gaps
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recommendations.map((rec) => (
                  <div key={rec.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <div className="flex items-center gap-2">
                            {getTypeIcon(rec.type)}
                            <h4 className="font-semibold">{rec.title}</h4>
                          </div>
                          <Badge variant="outline">{rec.type}</Badge>
                          <div className="flex items-center gap-1">
                            <Zap className="h-3 w-3 text-green-600" />
                            <span className="text-xs text-green-600">{rec.relevance_score}% match</span>
                          </div>
                        </div>
                        
                        <p className="text-sm text-muted-foreground mb-3">{rec.description}</p>
                        
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-3">
                          <div className="text-sm">
                            <span className="font-medium">Provider:</span> {rec.provider}
                          </div>
                          <div className="text-sm">
                            <span className="font-medium">Duration:</span> {rec.duration}
                          </div>
                          <div className="text-sm">
                            <span className="font-medium">Level:</span> {rec.difficulty}
                          </div>
                          <div className="text-sm">
                            <span className="font-medium">Cost:</span> {rec.cost}
                          </div>
                        </div>

                        <div className="flex flex-wrap gap-1">
                          <span className="text-sm text-muted-foreground mr-2">Skills:</span>
                          {rec.skills.map((skill, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div className="flex flex-col gap-2 min-w-[100px]">
                        <Button size="sm">Enroll</Button>
                        <Button size="sm" variant="outline">Learn More</Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="skill-gaps" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Skill Gap Analysis
              </CardTitle>
              <CardDescription>
                Identify and prioritize skills for development based on your career goals
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {skillGaps.map((skill, index) => (
                  <div key={index} className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <h4 className="font-medium">{skill.name}</h4>
                        <Badge variant="outline">{skill.category}</Badge>
                        <Badge className={getImportanceColor(skill.priority)}>
                          {skill.priority} Priority
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {skill.current_level}% → {skill.target_level}%
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>Current Level</span>
                        <span>Target Level</span>
                      </div>
                      <div className="relative">
                        <Progress value={skill.target_level} className="h-2 bg-muted" />
                        <Progress 
                          value={skill.current_level} 
                          className="absolute top-0 h-2" 
                        />
                        <div 
                          className={`target-level-indicator progress-${skill.target_level}`}
                        ></div>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span>0%</span>
                        <span>50%</span>
                        <span>100%</span>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        <Search className="h-3 w-3 mr-1" />
                        Find Courses
                      </Button>
                      <Button size="sm" variant="outline">
                        <Users className="h-3 w-3 mr-1" />
                        Find Mentor
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5" />
                AI Insights & Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                  <h5 className="font-medium text-blue-900 mb-2">Priority Focus Areas</h5>
                  <p className="text-sm text-blue-800">
                    Based on your career goals, focus on React and TypeScript skills first. 
                    These are essential for your target Senior Frontend Developer role.
                  </p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg border-l-4 border-green-400">
                  <h5 className="font-medium text-green-900 mb-2">Quick Wins</h5>
                  <p className="text-sm text-green-800">
                    Your React skills are already strong. A focused 4-week course could 
                    easily bridge the gap to your target level.
                  </p>
                </div>
                <div className="p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-400">
                  <h5 className="font-medium text-yellow-900 mb-2">Long-term Development</h5>
                  <p className="text-sm text-yellow-800">
                    Consider developing System Design and Leadership skills for future 
                    growth into Technical Lead or Architect roles.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="catalog" className="space-y-6">
          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="h-5 w-5" />
                Course Catalog
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <Label htmlFor="search">Search Courses</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="search"
                      placeholder="Search courses..."
                      className="pl-10"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div>
                  <Label>Category</Label>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      <SelectItem value="technical">Technical</SelectItem>
                      <SelectItem value="leadership">Leadership</SelectItem>
                      <SelectItem value="design">Design</SelectItem>
                      <SelectItem value="data">Data Science</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Difficulty</Label>
                  <Select value={selectedDifficulty} onValueChange={setSelectedDifficulty}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Levels</SelectItem>
                      <SelectItem value="beginner">Beginner</SelectItem>
                      <SelectItem value="intermediate">Intermediate</SelectItem>
                      <SelectItem value="advanced">Advanced</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end">
                  <Button className="w-full">
                    <Search className="h-4 w-4 mr-2" />
                    Search
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Course Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {learningPaths.map((path) => (
              <Card key={path.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Badge className={getDifficultyColor(path.difficulty)}>
                        {path.difficulty}
                      </Badge>
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4 text-yellow-500" />
                        <span className="text-sm">{path.rating}</span>
                      </div>
                    </div>
                    
                    <h3 className="font-semibold">{path.title}</h3>
                    <p className="text-sm text-muted-foreground">{path.description}</p>
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <span>{path.duration}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <BookOpen className="h-4 w-4 text-muted-foreground" />
                        <span>{path.total_modules} modules</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4 text-muted-foreground" />
                        <span>{path.enrollment_count} enrolled</span>
                      </div>
                    </div>
                    
                    <div className="flex flex-wrap gap-1">
                      {path.skills.slice(0, 3).map((skill, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                      {path.skills.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{path.skills.length - 3} more
                        </Badge>
                      )}
                    </div>
                    
                    <Button className="w-full" size="sm">
                      Enroll Now
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Learning Progress
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600 mb-2">
                      {Math.round(totalProgress)}%
                    </div>
                    <div className="text-sm text-muted-foreground">Overall Progress</div>
                  </div>
                  <Progress value={totalProgress} className="h-3" />
                  <div className="grid grid-cols-3 gap-4 text-center text-sm">
                    <div>
                      <div className="font-semibold">{completedPaths}</div>
                      <div className="text-muted-foreground">Completed</div>
                    </div>
                    <div>
                      <div className="font-semibold">{inProgressPaths}</div>
                      <div className="text-muted-foreground">In Progress</div>
                    </div>
                    <div>
                      <div className="font-semibold">{learningPaths.length - completedPaths - inProgressPaths}</div>
                      <div className="text-muted-foreground">Not Started</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Learning Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600 mb-2">12h</div>
                    <div className="text-sm text-muted-foreground">This Week</div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Daily Goal: 2h</span>
                      <span className="text-green-600">✓ 6/7 days</span>
                    </div>
                    <Progress value={85} className="h-2" />
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-center text-sm">
                    <div>
                      <div className="font-semibold">47h</div>
                      <div className="text-muted-foreground">This Month</div>
                    </div>
                    <div>
                      <div className="font-semibold">156h</div>
                      <div className="text-muted-foreground">All Time</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recent Achievements</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {achievements.map((achievement) => (
                  <div key={achievement.id} className="flex items-center gap-3 p-3 border rounded-lg">
                    <Award className="h-8 w-8 text-yellow-500" />
                    <div className="flex-1">
                      <p className="font-medium">{achievement.title}</p>
                      <p className="text-sm text-muted-foreground">{achievement.description}</p>
                    </div>
                    <span className="text-sm text-muted-foreground">{new Date(achievement.date_earned).toLocaleDateString()}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
