"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function AdminPanel() {
  const router = useRouter();
  const [isAdmin, setIsAdmin] = useState(false);
  const [isLoadingAuth, setIsLoadingAuth] = useState(true);

  // New item states
  const [newMapName, setNewMapName] = useState("");
  const [newMapImage, setNewMapImage] = useState("");
  
  const [newCarName, setNewCarName] = useState("");
  const [newCarClass, setNewCarClass] = useState("");
  const [newCarImage, setNewCarImage] = useState("");

  const [newPetName, setNewPetName] = useState("");
  const [newPetImage, setNewPetImage] = useState("");

  useEffect(() => {
    const checkAdmin = async () => {
      try {
        const res = await api.get("/auth/me");
        if (res.data.role === "ADMIN") {
          setIsAdmin(true);
        } else {
          toast.error("Access denied. Admins only.");
          router.push("/");
        }
      } catch (e) {
        router.push("/login");
      } finally {
        setIsLoadingAuth(false);
      }
    };
    checkAdmin();
  }, [router]);

  const { data: maps = [], refetch: refetchMaps } = useQuery({ queryKey: ["maps"], queryFn: async () => (await api.get("/maps")).data, enabled: isAdmin });
  const { data: cars = [], refetch: refetchCars } = useQuery({ queryKey: ["cars"], queryFn: async () => (await api.get("/cars")).data, enabled: isAdmin });
  const { data: pets = [], refetch: refetchPets } = useQuery({ queryKey: ["pets"], queryFn: async () => (await api.get("/pets")).data, enabled: isAdmin });
  const { data: users = [], refetch: refetchUsers } = useQuery({ queryKey: ["users"], queryFn: async () => (await api.get("/users")).data, enabled: isAdmin });

  const handleToggleUser = async (userId: string, currentStatus: boolean) => {
    try {
      await api.put(`/users/${userId}/admin`, { is_active: !currentStatus });
      toast.success(currentStatus ? "User locked" : "User unlocked");
      refetchUsers();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Failed to update user");
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!confirm("Are you sure you want to permanently delete this user? This cannot be undone.")) return;
    try {
      await api.delete(`/users/${userId}`);
      toast.success("User deleted");
      refetchUsers();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Failed to delete user");
    }
  };

  const handleAddMap = async () => {
    try {
      await api.post("/admin/maps", { name: newMapName, image: newMapImage || null });
      toast.success("Map added!");
      setNewMapName("");
      setNewMapImage("");
      refetchMaps();
    } catch (e) {
      toast.error("Failed to add map");
    }
  };

  const handleAddCar = async () => {
    try {
      await api.post("/admin/cars", { name: newCarName, car_class: newCarClass || "A", image: newCarImage || null });
      toast.success("Car added!");
      setNewCarName("");
      setNewCarClass("");
      setNewCarImage("");
      refetchCars();
    } catch (e) {
      toast.error("Failed to add car");
    }
  };

  const handleAddPet = async () => {
    try {
      await api.post("/admin/pets", { name: newPetName, image: newPetImage || null });
      toast.success("Pet added!");
      setNewPetName("");
      setNewPetImage("");
      refetchPets();
    } catch (e) {
      toast.error("Failed to add pet");
    }
  };

  if (isLoadingAuth) return <div className="text-center py-20 text-gray-400">Verifying access...</div>;
  if (!isAdmin) return null;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Admin Dashboard</h1>
        <p className="text-gray-400">Manage masters data (Maps, Cars, Pets) and system settings.</p>
      </div>

      <Tabs defaultValue="maps" className="w-full">
        <TabsList className="bg-gray-900 border-white/10">
          <TabsTrigger value="maps">Maps</TabsTrigger>
          <TabsTrigger value="cars">Cars</TabsTrigger>
          <TabsTrigger value="pets">Pets</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
        </TabsList>
        
        {/* Maps Tab */}
        <TabsContent value="maps" className="space-y-6 mt-6">
          <Card className="bg-gray-900/50 border-white/10">
            <CardHeader>
              <CardTitle>Add New Map</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col md:flex-row gap-4">
              <Input placeholder="Map Name" value={newMapName} onChange={(e) => setNewMapName(e.target.value)} className="bg-black/50 border-white/10" />
              <Input placeholder="Image URL (Optional)" value={newMapImage} onChange={(e) => setNewMapImage(e.target.value)} className="bg-black/50 border-white/10" />
              <Button onClick={handleAddMap} className="bg-blue-600 hover:bg-blue-500" disabled={!newMapName}>Add Map</Button>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/30 border-white/10 overflow-hidden">
            <Table>
              <TableHeader className="bg-black/40">
                <TableRow className="border-white/10">
                  <TableHead>Name</TableHead>
                  <TableHead>Image</TableHead>
                  <TableHead>ID</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {maps.map((map: any) => (
                  <TableRow key={map.id} className="border-white/5">
                    <TableCell className="font-medium">{map.name}</TableCell>
                    <TableCell>
                      {map.image ? <img src={map.image} alt={map.name} className="h-8 w-12 object-cover rounded" /> : "-"}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-gray-500">{map.id}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        {/* Cars Tab */}
        <TabsContent value="cars" className="space-y-6 mt-6">
          <Card className="bg-gray-900/50 border-white/10">
            <CardHeader>
              <CardTitle>Add New Car</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col md:flex-row gap-4">
              <Input placeholder="Car Name" value={newCarName} onChange={(e) => setNewCarName(e.target.value)} className="bg-black/50 border-white/10" />
              <Input placeholder="Class (e.g. S, A)" value={newCarClass} onChange={(e) => setNewCarClass(e.target.value)} className="bg-black/50 border-white/10 w-24" />
              <Input placeholder="Image URL (Optional)" value={newCarImage} onChange={(e) => setNewCarImage(e.target.value)} className="bg-black/50 border-white/10" />
              <Button onClick={handleAddCar} className="bg-orange-600 hover:bg-orange-500" disabled={!newCarName}>Add Car</Button>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/30 border-white/10 overflow-hidden">
            <Table>
              <TableHeader className="bg-black/40">
                <TableRow className="border-white/10">
                  <TableHead>Name</TableHead>
                  <TableHead>Class</TableHead>
                  <TableHead>Image</TableHead>
                  <TableHead>ID</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {cars.map((car: any) => (
                  <TableRow key={car.id} className="border-white/5">
                    <TableCell className="font-medium">{car.name}</TableCell>
                    <TableCell>{car.car_class}</TableCell>
                    <TableCell>
                      {car.image ? <img src={car.image} alt={car.name} className="h-8 w-12 object-cover rounded" /> : "-"}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-gray-500">{car.id}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        {/* Pets Tab */}
        <TabsContent value="pets" className="space-y-6 mt-6">
          <Card className="bg-gray-900/50 border-white/10">
            <CardHeader>
              <CardTitle>Add New Pet</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col md:flex-row gap-4">
              <Input placeholder="Pet Name" value={newPetName} onChange={(e) => setNewPetName(e.target.value)} className="bg-black/50 border-white/10" />
              <Input placeholder="Image URL (Optional)" value={newPetImage} onChange={(e) => setNewPetImage(e.target.value)} className="bg-black/50 border-white/10" />
              <Button onClick={handleAddPet} className="bg-purple-600 hover:bg-purple-500" disabled={!newPetName}>Add Pet</Button>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/30 border-white/10 overflow-hidden">
            <Table>
              <TableHeader className="bg-black/40">
                <TableRow className="border-white/10">
                  <TableHead>Name</TableHead>
                  <TableHead>Image</TableHead>
                  <TableHead>ID</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pets.map((pet: any) => (
                  <TableRow key={pet.id} className="border-white/5">
                    <TableCell className="font-medium">{pet.name}</TableCell>
                    <TableCell>
                      {pet.image ? <img src={pet.image} alt={pet.name} className="h-8 w-8 object-cover rounded-full" /> : "-"}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-gray-500">{pet.id}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-6 mt-6">
          <Card className="bg-gray-900/30 border-white/10 overflow-hidden">
            <Table>
              <TableHeader className="bg-black/40">
                <TableRow className="border-white/10">
                  <TableHead>Avatar</TableHead>
                  <TableHead>Username</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user: any) => (
                  <TableRow key={user.id} className="border-white/5">
                    <TableCell>
                      {user.avatar ? (
                        <img src={user.avatar} alt={user.username} className="h-8 w-8 object-cover rounded-full" />
                      ) : (
                        <div className="h-8 w-8 bg-gray-800 rounded-full" />
                      )}
                    </TableCell>
                    <TableCell className="font-medium">{user.username}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <span className={`px-2 py-1 text-xs rounded-full ${user.role === 'ADMIN' ? 'bg-purple-900 text-purple-300' : 'bg-gray-800 text-gray-300'}`}>
                        {user.role}
                      </span>
                    </TableCell>
                    <TableCell>
                      <span className={`px-2 py-1 text-xs rounded-full ${user.is_active ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
                        {user.is_active ? 'Active' : 'Locked'}
                      </span>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => handleToggleUser(user.id, user.is_active)}
                          className={user.is_active ? 'text-red-500 hover:text-red-400' : 'text-green-500 hover:text-green-400'}
                        >
                          {user.is_active ? 'Lock' : 'Unlock'}
                        </Button>
                        <Button 
                          variant="destructive" 
                          size="sm" 
                          onClick={() => handleDeleteUser(user.id)}
                          disabled={user.role === 'ADMIN'}
                        >
                          Delete
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

      </Tabs>
    </div>
  );
}
