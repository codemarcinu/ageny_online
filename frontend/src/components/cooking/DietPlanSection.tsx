import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Calculator, 
  Utensils, 
  Apple, 
  Target, 
  TrendingUp, 
  Clock,
  Heart,
  Zap
} from 'lucide-react';

interface MealPlan {
  daily_calories: number;
  daily_proteins: number;
  daily_carbs: number;
  daily_fats: number;
  meals: Array<{
    name: string;
    calories: number;
    proteins: number;
    carbs: number;
    fats: number;
    ingredients: string[];
    prep_time: number;
  }>;
  shopping_list: Array<{
    name: string;
    quantity: string;
    estimated_price: number;
  }>;
  estimated_cost: number;
  nutrition_tips: string[];
}

interface BMICalculation {
  bmi: number;
  bmi_category: string;
  healthy_weight_range: {
    min: number;
    max: number;
  };
  recommendations: string[];
}

const DietPlanSection: React.FC = () => {
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [bmiResult, setBmiResult] = useState<BMICalculation | null>(null);
  const [loading, setLoading] = useState(false);

  // Form states
  const [mealPlanForm, setMealPlanForm] = useState({
    age: 14,
    weight: 50,
    height: 160,
    activity_level: 'średni',
    dietary_restrictions: '',
    preferences: '',
    budget_per_day: 30
  });

  const [bmiForm, setBmiForm] = useState({
    weight: 50,
    height: 160,
    age: 14
  });

  const generateMealPlan = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v2/cooking/meal-plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...mealPlanForm,
          dietary_restrictions: mealPlanForm.dietary_restrictions ? 
            mealPlanForm.dietary_restrictions.split(',').map(s => s.trim()) : undefined
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setMealPlan(data);
      } else {
        console.error('Failed to generate meal plan');
      }
    } catch (error) {
      console.error('Error generating meal plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateBMI = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v2/cooking/bmi', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bmiForm),
      });

      if (response.ok) {
        const data = await response.json();
        setBmiResult(data);
      } else {
        console.error('Failed to calculate BMI');
      }
    } catch (error) {
      console.error('Error calculating BMI:', error);
    } finally {
      setLoading(false);
    }
  };

  const getBMICategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'niedowaga':
        return 'bg-blue-100 text-blue-800';
      case 'prawidłowa waga':
        return 'bg-green-100 text-green-800';
      case 'nadwaga':
        return 'bg-yellow-100 text-yellow-800';
      case 'otyłość':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2">
        <Apple className="h-6 w-6 text-green-600" />
        <h2 className="text-2xl font-bold text-gray-900">Planowanie Diety</h2>
      </div>

      <Tabs className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="meal-plan" className="flex items-center space-x-2">
            <Utensils className="h-4 w-4" />
            <span>Plan Posiłków</span>
          </TabsTrigger>
          <TabsTrigger value="bmi" className="flex items-center space-x-2">
            <Calculator className="h-4 w-4" />
            <span>Kalkulator BMI</span>
          </TabsTrigger>
          <TabsTrigger value="tips" className="flex items-center space-x-2">
            <Heart className="h-4 w-4" />
            <span>Porady</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="h-5 w-5" />
                <span>Generuj Plan Posiłków</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="age">Wiek</Label>
                  <Input
                    id="age"
                    type="number"
                    value={mealPlanForm.age}
                    onChange={(e) => setMealPlanForm(prev => ({ ...prev, age: parseInt(e.target.value) }))}
                    min="10"
                    max="18"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="weight">Waga (kg)</Label>
                  <Input
                    id="weight"
                    type="number"
                    value={mealPlanForm.weight}
                    onChange={(e) => setMealPlanForm(prev => ({ ...prev, weight: parseFloat(e.target.value) }))}
                    min="30"
                    max="100"
                    step="0.1"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="height">Wzrost (cm)</Label>
                  <Input
                    id="height"
                    type="number"
                    value={mealPlanForm.height}
                    onChange={(e) => setMealPlanForm(prev => ({ ...prev, height: parseFloat(e.target.value) }))}
                    min="120"
                    max="200"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="activity">Poziom Aktywności</Label>
                  <Select
                    value={mealPlanForm.activity_level}
                    onValueChange={(value) => setMealPlanForm(prev => ({ ...prev, activity_level: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="niski">Niski (siedzący tryb życia)</SelectItem>
                      <SelectItem value="średni">Średni (lekka aktywność)</SelectItem>
                      <SelectItem value="wysoki">Wysoki (sport, aktywność)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="restrictions">Ograniczenia Dietetyczne</Label>
                <Textarea
                  id="restrictions"
                  placeholder="np. bezglutenowe, wegetariańskie, alergia na orzechy..."
                  value={mealPlanForm.dietary_restrictions}
                  onChange={(e) => setMealPlanForm(prev => ({ ...prev, dietary_restrictions: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="preferences">Preferencje Smakowe</Label>
                <Textarea
                  id="preferences"
                  placeholder="np. lubię pikantne, preferuję słodkie, nie lubię ryb..."
                  value={mealPlanForm.preferences}
                  onChange={(e) => setMealPlanForm(prev => ({ ...prev, preferences: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="budget">Budżet Dzienny (PLN)</Label>
                <Input
                  id="budget"
                  type="number"
                  value={mealPlanForm.budget_per_day}
                  onChange={(e) => setMealPlanForm(prev => ({ ...prev, budget_per_day: parseFloat(e.target.value) }))}
                  min="0"
                  step="5"
                />
              </div>

              <Button 
                onClick={generateMealPlan} 
                disabled={loading}
                className="w-full"
              >
                {loading ? 'Generuję plan...' : 'Generuj Plan Posiłków'}
              </Button>
            </CardContent>
          </Card>

          {mealPlan && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="h-5 w-5" />
                  <span>Twój Plan Posiłków</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Nutrition Summary */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{mealPlan.daily_calories}</div>
                    <div className="text-sm text-gray-600">Kalorie</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{mealPlan.daily_proteins}g</div>
                    <div className="text-sm text-gray-600">Białka</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-600">{mealPlan.daily_carbs}g</div>
                    <div className="text-sm text-gray-600">Węglowodany</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">{mealPlan.daily_fats}g</div>
                    <div className="text-sm text-gray-600">Tłuszcze</div>
                  </div>
                </div>

                {/* Meals */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Posiłki</h3>
                  {mealPlan.meals.map((meal, index) => (
                    <Card key={index} className="border-l-4 border-l-green-500">
                      <CardContent className="pt-4">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h4 className="font-semibold text-lg">{meal.name}</h4>
                            <div className="flex items-center space-x-2 mt-2">
                              <Clock className="h-4 w-4 text-gray-500" />
                              <span className="text-sm text-gray-600">{meal.prep_time} min</span>
                            </div>
                            <div className="mt-2">
                              <div className="text-sm text-gray-600">Składniki:</div>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {meal.ingredients.map((ingredient, idx) => (
                                  <Badge key={idx} variant="secondary" className="text-xs">
                                    {ingredient}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-semibold">{meal.calories} kcal</div>
                            <div className="text-sm text-gray-600">
                              B: {meal.proteins}g | W: {meal.carbs}g | T: {meal.fats}g
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* Shopping List */}
                {mealPlan.shopping_list.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Lista Zakupów</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {mealPlan.shopping_list.map((item, index) => (
                        <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                          <span className="font-medium">{item.name}</span>
                          <span className="text-sm text-gray-600">{item.quantity}</span>
                        </div>
                      ))}
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold">
                        Szacowany koszt: {mealPlan.estimated_cost} PLN
                      </div>
                    </div>
                  </div>
                )}

                {/* Nutrition Tips */}
                {mealPlan.nutrition_tips.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Porady Żywieniowe</h3>
                    <div className="space-y-2">
                      {mealPlan.nutrition_tips.map((tip, index) => (
                        <div key={index} className="flex items-start space-x-2 p-3 bg-blue-50 rounded-lg">
                          <Heart className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                          <span className="text-sm">{tip}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calculator className="h-5 w-5" />
                <span>Kalkulator BMI</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="bmi-weight">Waga (kg)</Label>
                  <Input
                    id="bmi-weight"
                    type="number"
                    value={bmiForm.weight}
                    onChange={(e) => setBmiForm(prev => ({ ...prev, weight: parseFloat(e.target.value) }))}
                    min="30"
                    max="100"
                    step="0.1"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="bmi-height">Wzrost (cm)</Label>
                  <Input
                    id="bmi-height"
                    type="number"
                    value={bmiForm.height}
                    onChange={(e) => setBmiForm(prev => ({ ...prev, height: parseFloat(e.target.value) }))}
                    min="120"
                    max="200"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="bmi-age">Wiek</Label>
                  <Input
                    id="bmi-age"
                    type="number"
                    value={bmiForm.age}
                    onChange={(e) => setBmiForm(prev => ({ ...prev, age: parseInt(e.target.value) }))}
                    min="10"
                    max="18"
                  />
                </div>
              </div>

              <Button 
                onClick={calculateBMI} 
                disabled={loading}
                className="w-full"
              >
                {loading ? 'Obliczam...' : 'Oblicz BMI'}
              </Button>
            </CardContent>
          </Card>

          {bmiResult && (
            <Card>
              <CardHeader>
                <CardTitle>Wyniki BMI</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-600">{bmiResult.bmi}</div>
                  <div className="text-lg text-gray-600">Twoje BMI</div>
                </div>

                <div className="text-center">
                  <Badge className={`text-lg px-4 py-2 ${getBMICategoryColor(bmiResult.bmi_category)}`}>
                    {bmiResult.bmi_category}
                  </Badge>
                </div>

                <div className="space-y-2">
                  <h4 className="font-semibold">Zakres zdrowej wagi:</h4>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <span className="font-medium">
                      {bmiResult.healthy_weight_range.min} - {bmiResult.healthy_weight_range.max} kg
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-semibold">Rekomendacje:</h4>
                  <div className="space-y-2">
                    {bmiResult.recommendations.map((recommendation, index) => (
                      <div key={index} className="flex items-start space-x-2 p-2 bg-blue-50 rounded">
                        <TrendingUp className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{recommendation}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Heart className="h-5 w-5" />
                <span>Porady Żywieniowe dla Nastolatków</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">Podstawowe Zasady</h3>
                  <div className="space-y-2">
                    <div className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm">Jedz regularnie 5 posiłków dziennie</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm">Pij dużo wody (minimum 2 litry)</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm">Jedz kolorowe warzywa i owoce</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm">Nie pomijaj śniadania</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">Czego Unikać</h3>
                  <div className="space-y-2">
                    <div className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm">Słodycze i fast food</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm">Słodkie napoje</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm">Jedzenie przed snem</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm">Siedzący tryb życia</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">Pamiętaj!</h4>
                <p className="text-sm text-blue-800">
                  Ruszaj się przynajmniej godzinę dziennie, jedz powoli i ciesz się jedzeniem. 
                  Każdy organizm jest inny, więc słuchaj swojego ciała!
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DietPlanSection; 