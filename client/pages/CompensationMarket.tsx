import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DollarSign, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Users, BarChart3, Target, Scale, Award, Filter, Download, RefreshCw, Eye, Lightbulb, Building, MapPin, Calendar, Search, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
  }).format(amount);
};

const formatPercent = (val: number | null | undefined) => {
  if (val === null || val === undefined) return "N/A";
  return val >= 0 ? `+${val.toFixed(1)}%` : `${val.toFixed(1)}%`;
};

export default function CompensationMarket() {
  const [selectedRole, setSelectedRole] = useState("");
  const [selectedLocation, setSelectedLocation] = useState("Remote");
  const [experienceLevel, setExperienceLevel] = useState("mid");
  const [marketData, setMarketData] = useState<any[]>([]);
  const [benchmark, setBenchmark] = useState<any>(null);
  const [payEquity, setPayEquity] = useState<any>(null);
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("market-data");
  const { toast } = useToast();

  const roles = [
    "Software Engineer",
    "Senior Software Engineer",
    "Product Manager",
    "Data Scientist",
    "DevOps Engineer",
    "Engineering Manager",
    "QA Engineer",
    "UX Designer",
    "Sales Engineer",
    "Technical Program Manager",
  ];

  const locations = [
    "San Francisco, CA",
    "New York, NY",
    "Seattle, WA",
    "Austin, TX",
    "Boston, MA",
    "Los Angeles, CA",
    "Chicago, IL",
    "Denver, CO",
    "Atlanta, GA",
    "Remote",
    "National Average",
  ];

  const experienceLevels = [
    { value: "junior", label: "Junior (0-2 years)" },
    { value: "mid", label: "Mid (2-5 years)" },
    { value: "senior", label: "Senior (5-8 years)" },
    { value: "lead", label: "Lead (8-12 years)" },
    { value: "manager", label: "Manager (10+ years)" },
  ];

  const fetchMarketData = async () => {
    if (!selectedRole) return;
    setLoading(true);
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_URL}/compensation/market-data?role=${encodeURIComponent(selectedRole)}&location=${encodeURIComponent(selectedLocation)}&experience_level=${experienceLevel}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setMarketData(data);
      }
    } catch (err) {
      console.error("Failed to fetch market data:", err);
      toast({ title: "Error", description: "Failed to load market data", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const fetchBenchmark = async () => {
    if (!selectedRole) return;
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_URL}/compensation/benchmark`, {
        method: "POST",
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          role: selectedRole,
          location: selectedLocation,
          experience_level: experienceLevel,
          internal_salaries: [],
        }),
      });
      if (response.ok) {
        const data = await response.json();
        setBenchmark(data);
      }
    } catch (err) {
      console.error("Failed to fetch benchmark:", err);
    }
  };

  const fetchPayEquity = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_URL}/compensation/pay-equity-analysis`, {
        method: "POST",
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ department: undefined }),
      });
      if (response.ok) {
        const data = await response.json();
        setPayEquity(data);
      }
    } catch (err) {
      console.error("Failed to fetch pay equity:", err);
    }
  };

  const fetchTrends = async () => {
    if (!selectedRole) return;
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_URL}/compensation/market-trends?role=${encodeURIComponent(selectedRole)}&location=${encodeURIComponent(selectedLocation)}&months=12`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setTrends(data);
      }
    } catch (err) {
      console.error("Failed to fetch trends:", err);
    }
  };

  useEffect(() => {
    fetchMarketData();
    fetchBenchmark();
    fetchPayEquity();
    fetchTrends();
  }, [selectedRole, selectedLocation, experienceLevel]);

  const getVarianceColor = (variance: number | null | undefined) => {
    if (variance === null || variance === undefined) return "text-gray-600";
    if (variance < -10) return "text-red-600";
    if (variance > 10) return "text-green-600";
    return "text-blue-600";
  };

  const getCompetitivenessColor = (comp: string) => {
    switch (comp) {
      case "Above Market": return "text-green-600 bg-green-100";
      case "At Market": return "text-blue-600 bg-blue-100";
      case "Below Market": return "text-red-600 bg-red-100";
      default: return "text-gray-600 bg-gray-100";
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <DollarSign className="h-7 w-7 text-emerald-500" />
            Compensation Market Intelligence
          </h1>
          <p className="text-muted-foreground">Market benchmarking, pay equity analysis, and compensation insights</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Analysis Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div>
              <Label>Role</Label>
              <Select value={selectedRole} onValueChange={setSelectedRole}>
                <SelectTrigger>
                  <SelectValue placeholder="Select role" />
                </SelectTrigger>
                <SelectContent>
                  {roles.map(role => (
                    <SelectItem key={role} value={role}>{role}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Location</Label>
              <Select value={selectedLocation} onValueChange={setSelectedLocation}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {locations.map(loc => (
                    <SelectItem key={loc} value={loc}>{loc}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Experience Level</Label>
              <Select value={experienceLevel} onValueChange={setExperienceLevel}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {experienceLevels.map(l => (
                    <SelectItem key={l.value} value={l.value}>{l.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button onClick={fetchMarketData} disabled={loading}>
                <RefreshCw className={loading ? "h-4 w-4 animate-spin mr-2" : "h-4 w-4 mr-2"} />
                Refresh Data
              </Button>
            </div>
            <div className="flex items-end">
              <Button variant="outline" onClick={() => { fetchMarketData(); fetchBenchmark(); fetchPayEquity(); fetchTrends(); }}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Full Refresh
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="market-data">Market Data</TabsTrigger>
          <TabsTrigger value="benchmark">Benchmark</TabsTrigger>
          <TabsTrigger value="pay-equity">Pay Equity</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
        </TabsList>

        <TabsContent value="market-data" className="space-y-6">
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : marketData.length === 0 ? (
            <Card className="text-center py-12">
              <CardContent>
                <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No market data available</h3>
                <p className="text-muted-foreground">Select a role and location to fetch market data</p>
              </CardContent>
            </Card>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {marketData.slice(0, 3).map((data, idx) => (
                  <Card key={idx}>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        {data.title}
                        <Badge variant="outline">{data.source}</Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <div className="text-2xl font-bold">{formatCurrency(data.percentile_25)}</div>
                          <div className="text-sm text-muted-foreground">25th Percentile</div>
                        </div>
                        <div>
                          <div className="text-2xl font-bold text-emerald-600">{formatCurrency(data.median_salary)}</div>
                          <div className="text-sm text-muted-foreground">Median</div>
                        </div>
                        <div>
                          <div className="text-2xl font-bold">{formatCurrency(data.percentile_75)}</div>
                          <div className="text-sm text-muted-foreground">75th Percentile</div>
                        </div>
                      </div>
                      <div className="mt-4 flex justify-between text-sm text-muted-foreground">
                        <span>Min: {formatCurrency(data.min_salary)}</span>
                        <span>Max: {formatCurrency(data.max_salary)}</span>
                      </div>
                      <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                        <span>Sample: {data.sample_size}</span>
                        <span>Updated: {new Date(data.date_collected).toLocaleDateString()}</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>All Market Data Points</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-3">Source</th>
                          <th className="text-left p-3">Title</th>
                          <th className="text-left p-3">Location</th>
                          <th className="text-right p-3">25th</th>
                          <th className="text-right p-3">Median</th>
                          <th className="text-right p-3">75th</th>
                          <th className="text-left p-3">Sample</th>
                        </tr>
                      </thead>
                      <tbody>
                        {marketData.map((data, idx) => (
                          <tr key={idx} className="border-b hover:bg-muted/50">
                            <td className="p-3">
                              <Badge variant="outline">{data.source}</Badge>
                            </td>
                            <td className="p-3 font-medium">{data.title}</td>
                            <td className="p-3 text-muted-foreground">{data.location}</td>
                            <td className="text-right p-3">{formatCurrency(data.percentile_25)}</td>
                            <td className="text-right p-3 font-medium">{formatCurrency(data.median_salary)}</td>
                            <td className="text-right p-3">{formatCurrency(data.percentile_75)}</td>
                            <td className="p-3 text-muted-foreground">{data.sample_size}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
</>
          )}
        </TabsContent>

        <TabsContent value="benchmark" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Market Benchmark
              </CardTitle>
              <CardDescription>Compare internal compensation against market rates</CardDescription>
            </CardHeader>
            <CardContent>
              {benchmark ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card>
                      <CardContent className="pt-6 text-center">
                        <div className="text-3xl font-bold text-emerald-600">{formatCurrency(benchmark.market_median)}</div>
                        <div className="text-sm text-muted-foreground">Market Median</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6 text-center">
                        <div className="text-3xl font-bold text-blue-600">{formatCurrency(benchmark.market_p25)}</div>
                        <div className="text-sm text-muted-foreground">25th Percentile</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6 text-center">
                        <div className="text-3xl font-bold text-orange-600">{formatCurrency(benchmark.market_p75)}</div>
                        <div className="text-sm text-muted-foreground">75th Percentile</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6 text-center">
                        <div className="text-3xl font-bold text-purple-600">{formatPercent(benchmark.variance_pct)}</div>
                        <div className="text-sm text-muted-foreground">Variance</div>
                      </CardContent>
                    </Card>
                  </div>

                  {benchmark.internal_median && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Internal vs Market Comparison</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="text-center p-4 bg-blue-50 rounded-lg">
                            <div className="text-2xl font-bold text-blue-600">{formatCurrency(benchmark.internal_median!)}</div>
                            <div className="text-sm text-muted-foreground">Internal Median</div>
                          </div>
                          <div className="text-center p-4 bg-emerald-50 rounded-lg">
                            <div className="text-2xl font-bold text-emerald-600">{formatCurrency(benchmark.market_median)}</div>
                            <div className="text-sm text-muted-foreground">Market Median</div>
                          </div>
                          <div className="text-center p-4 bg-purple-50 rounded-lg">
                            <div className="text-2xl font-bold text-purple-600">{formatPercent(benchmark.variance_pct)}</div>
                            <div className="text-sm text-muted-foreground">Variance</div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  <Card>
                    <CardHeader>
                      <CardTitle>Market Position</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-center gap-4">
                        <div className="relative w-64 h-8">
                          <div className="absolute inset-0 bg-gradient-to-r from-red-200 via-yellow-200 to-green-200 rounded-full" />
                          <div
                            className="absolute top-0 h-8 w-2 bg-blue-600 rounded-full"
                            style={{
                              left: `${Math.max(0, Math.min(100, ((benchmark.internal_median || benchmark.market_median) - benchmark.market_p25) / (benchmark.market_p75 - benchmark.market_p25) * 100))}%`,
                            }}
                          ></div>
                        </div>
                        <div className="flex gap-8 text-sm text-muted-foreground">
                          <span>P25: {formatCurrency(benchmark.market_p25)}</span>
                          <span>P75: {formatCurrency(benchmark.market_p75)}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Metadata</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <div className="text-lg font-bold">{benchmark.data_points}</div>
                          <div className="text-sm text-muted-foreground">Data Points</div>
                        </div>
                        <div>
                          <div className="text-lg font-bold">{benchmark.sources.join(", ")}</div>
                          <div className="text-sm text-muted-foreground">Sources</div>
                        </div>
                        <div>
                          <div className="text-lg font-bold">{benchmark.location}</div>
                          <div className="text-sm text-muted-foreground">Location</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Target className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">Select a role to view benchmark</h3>
                  <p className="text-muted-foreground">Choose a role from the filters above</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pay-equity" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Pay Equity Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Pay equity analysis will appear here when data is available.</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Market Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Market trend data will appear here when a role is selected.</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">AI-powered recommendations will appear here after analysis.</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}