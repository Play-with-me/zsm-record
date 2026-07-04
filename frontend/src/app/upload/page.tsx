"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { FormCombobox } from "@/components/form-combobox";
import { toast } from "sonner";

// Validation for format m:ss.mmm
const recordRegex = /^\d+:\d{2}\.\d{3}$/;

const uploadSchema = z.object({
  video_url: z.string().url("Must be a valid URL"),
  map_id: z.string().min(1, "Map is required"),
  car_id: z.string().min(1, "Car is required"),
  pet_id: z.string().optional(),
  record_str: z.string().regex(recordRegex, "Format must be m:ss.mmm (e.g., 1:28.456)"),
  description: z.string().optional(),
  visibility: z.enum(["PUBLIC", "PRIVATE"])
});

export default function UploadPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: maps = [] } = useQuery({ queryKey: ["maps"], queryFn: async () => (await api.get("/maps")).data });
  const { data: cars = [] } = useQuery({ queryKey: ["cars"], queryFn: async () => (await api.get("/cars")).data });
  const { data: pets = [] } = useQuery({ queryKey: ["pets"], queryFn: async () => (await api.get("/pets")).data });

  const form = useForm<z.infer<typeof uploadSchema>>({
    resolver: zodResolver(uploadSchema),
    defaultValues: {
      video_url: "",
      map_id: "",
      car_id: "",
      pet_id: "",
      record_str: "",
      description: "",
      visibility: "PUBLIC"
    },
  });

  const parseRecordToMs = (recordStr: string) => {
    const [minutes, rest] = recordStr.split(":");
    const [seconds, milliseconds] = rest.split(".");
    return (parseInt(minutes) * 60 * 1000) + (parseInt(seconds) * 1000) + parseInt(milliseconds);
  };

  async function onSubmit(values: z.infer<typeof uploadSchema>) {
    setIsSubmitting(true);
    try {
      const record_ms = parseRecordToMs(values.record_str);
      
      const payload = {
        video_url: values.video_url,
        map_id: values.map_id,
        car_id: values.car_id,
        pet_id: values.pet_id || null,
        record_ms: record_ms,
        description: values.description,
        visibility: values.visibility
      };

      await api.post("/videos", payload);
      toast.success("Record uploaded successfully!");
      router.push("/");
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error("Please login to upload a record");
        router.push("/login");
      } else {
        toast.error("Failed to upload record");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  const mapOptions = maps.map((m: any) => ({ label: m.name, value: m.id }));
  const carOptions = cars.map((c: any) => ({ label: c.name, value: c.id }));
  const petOptions = pets.map((p: any) => ({ label: p.name, value: p.id }));

  return (
    <div className="max-w-2xl mx-auto py-8">
      <Card className="bg-gray-900/40 border-white/10 backdrop-blur-md">
        <CardHeader>
          <CardTitle className="text-3xl font-bold tracking-tight">Upload Record</CardTitle>
          <CardDescription className="text-gray-400">Share your best time with the community.</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              
              <FormField
                control={form.control}
                name="video_url"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Video URL</FormLabel>
                    <FormControl>
                      <Input placeholder="https://youtube.com/watch?v=..." {...field} className="bg-black/50 border-white/10" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="map_id"
                  render={({ field }) => (
                    <FormItem className="flex flex-col">
                      <FormLabel>Map</FormLabel>
                      <FormCombobox 
                        options={mapOptions} 
                        value={field.value} 
                        onChange={field.onChange} 
                        placeholder="Search Map..." 
                      />
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="car_id"
                  render={({ field }) => (
                    <FormItem className="flex flex-col">
                      <FormLabel>Car</FormLabel>
                      <FormCombobox 
                        options={carOptions} 
                        value={field.value} 
                        onChange={field.onChange} 
                        placeholder="Search Car..." 
                      />
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="record_str"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Record Time</FormLabel>
                      <FormControl>
                        <Input placeholder="1:28.456" {...field} className="bg-black/50 border-white/10 font-mono" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="pet_id"
                  render={({ field }) => (
                    <FormItem className="flex flex-col">
                      <FormLabel>Pet (Optional)</FormLabel>
                      <FormCombobox 
                        options={petOptions} 
                        value={field.value || ""} 
                        onChange={field.onChange} 
                        placeholder="Search Pet..." 
                      />
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="visibility"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Visibility</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger className="bg-black/50 border-white/10">
                          <SelectValue placeholder="Select visibility" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="bg-gray-900 border-white/10">
                        <SelectItem value="PUBLIC">Public - Everyone can see</SelectItem>
                        <SelectItem value="PRIVATE">Private - Only me and Admins</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description (Optional)</FormLabel>
                    <FormControl>
                      <Textarea placeholder="Any notes about this run?" {...field} className="bg-black/50 border-white/10 min-h-[100px]" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-500 font-semibold" disabled={isSubmitting}>
                {isSubmitting ? "Uploading..." : "Upload Record"}
              </Button>

            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
