ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker'
 
Vagrant.configure("2") do |config|
  config.vm.define "paverdev" do |a|
    a.vm.provider "docker" do |d|
      d.build_dir = "."
      d.build_args = ["-t=paverdev"]
      d.name = "paverdev"
      d.remains_running = true
      d.cmd = ["paver", "test"]
      d.volumes = ["/paver-base:/paver-venv"]
    end
  end
end