ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker'
 
Vagrant.configure("2") do |config|

  config.vm.synced_folder ".", "/paver-base"

  config.vm.network "private_network", ip: "10.7.7.7"

  config.vm.define "paverdev" do |a|
    a.vm.provider "docker" do |d|

      d.build_dir = "."
      d.build_args = ["-t=paverdev"]

      d.name = "paverdev"
      d.remains_running = true

      d.cmd = ["/usr/sbin/sshd", "-D"]
      # d.cmd = ["/bin/bash"]
      # d.entrypoint = ["paver", "-v"]

      # d.volumes = ["/paver-base:/paver-venv"]

      d.vagrant_machine = "dockerhost"
      d.vagrant_vagrantfile = "./DockerHostVagrantfile"

    end
  end
end
